"""Seed, benchmark, and safely remove product performance-test data.

This script works directly against the configured database and Redis instance.
All generated products are namespaced with a unique run ID, so cleanup never
uses a broad delete condition.
"""

from __future__ import annotations

import argparse
import math
import re
import statistics
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Sequence

from redis.exceptions import RedisError
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.infrastructure.database import SessionLocal, engine  # noqa: E402
from app.infrastructure.models.activity_log_model import (  # noqa: E402
    ActivityLogModel,
)
from app.infrastructure.models.product_detail_model import (  # noqa: E402
    ProductDetailModel,
)
from app.infrastructure.models.product_model import ProductModel  # noqa: E402
from app.infrastructure.models.product_tag_model import product_tags  # noqa: E402
from app.infrastructure.models.profile_model import ProfileModel  # noqa: E402,F401
from app.infrastructure.models.tag_model import TagModel  # noqa: E402,F401
from app.infrastructure.models.user_model import UserModel  # noqa: E402
from app.infrastructure.redis_client import redis_client  # noqa: E402
from app.infrastructure.repositories.redis_product_cache_repository import (  # noqa: E402
    RedisProductCacheRepository,
)
from app.infrastructure.repositories.sqlalchemy_product_repository import (  # noqa: E402
    SQLAlchemyProductRepository,
)


MARKER_PREFIX = "PERFTEST-"
RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9-]{1,40}$")
DEFAULT_COUNT = 10_000
DEFAULT_BATCH_SIZE = 1_000


@dataclass(frozen=True)
class Measurement:
    name: str
    runs: int
    minimum_ms: float
    average_ms: float
    median_ms: float
    p95_ms: float
    maximum_ms: float


def create_run_id() -> str:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    return f"{timestamp}-{uuid.uuid4().hex[:8]}"


def validate_run_id(run_id: str) -> str:
    if RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ValueError(
            "run_id yalnızca harf, rakam ve tire içerebilir "
            "ve en fazla 40 karakter olabilir."
        )

    return run_id


def marker_for(run_id: str) -> str:
    return f"{MARKER_PREFIX}{validate_run_id(run_id)}-"


def chunked(values: Sequence[str], size: int = 500):
    for start in range(0, len(values), size):
        yield values[start : start + size]


def resolve_owner(
    db: Session,
    owner_email: str | None,
) -> UserModel:
    query = db.query(UserModel).filter(
        UserModel.is_active.is_(True)
    )

    if owner_email is not None:
        owner = query.filter(
            func.lower(UserModel.email)
            == owner_email.strip().lower()
        ).first()
    else:
        owner = query.order_by(UserModel.id.asc()).first()

    if owner is None:
        if owner_email is None:
            message = (
                "Aktif kullanıcı bulunamadı. Önce bir kullanıcı oluşturun "
                "veya --owner-email ile aktif bir kullanıcı seçin."
            )
        else:
            message = (
                f"Aktif kullanıcı bulunamadı: {owner_email}"
            )

        raise RuntimeError(message)

    return owner


def count_products(db: Session, run_id: str) -> int:
    marker = marker_for(run_id)

    return (
        db.query(ProductModel)
        .filter(ProductModel.name.like(f"{marker}%"))
        .count()
    )


def seed_products(
    db: Session,
    *,
    run_id: str,
    count: int,
    batch_size: int,
    owner_email: str | None,
) -> tuple[int, float, str]:
    if count < 1:
        raise ValueError("count en az 1 olmalıdır.")

    if batch_size < 1:
        raise ValueError("batch_size en az 1 olmalıdır.")

    marker = marker_for(run_id)

    if count_products(db, run_id) > 0:
        raise RuntimeError(
            f"{run_id} run_id için test verisi zaten mevcut."
        )

    owner = resolve_owner(db, owner_email)
    started_at = time.perf_counter()

    try:
        for start in range(0, count, batch_size):
            end = min(start + batch_size, count)
            rows = []

            for index in range(start, end):
                rows.append(
                    {
                        "public_id": str(uuid.uuid4()),
                        "owner_id": owner.id,
                        "name": (
                            f"{marker}product-{index:06d}"
                        ),
                        "price": round(
                            1 + ((index * 17) % 250_000) / 100,
                            2,
                        ),
                        "stock": (index * 37) % 5_000,
                        "is_deleted": False,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now(),
                    }
                )

            db.bulk_insert_mappings(ProductModel, rows)

        db.commit()
    except Exception:
        db.rollback()
        raise

    elapsed_seconds = time.perf_counter() - started_at
    inserted = count_products(db, run_id)

    if inserted != count:
        raise RuntimeError(
            f"Beklenen {count} kayıt yerine {inserted} kayıt eklendi."
        )

    return inserted, elapsed_seconds, owner.email


def percentile(values: list[float], ratio: float) -> float:
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * ratio) - 1)
    return ordered[index]


def measure(
    name: str,
    operation: Callable[[], object],
    *,
    iterations: int,
    warmups: int = 1,
) -> Measurement:
    if iterations < 1:
        raise ValueError("iterations en az 1 olmalıdır.")

    for _ in range(warmups):
        operation()

    durations_ms = []

    for _ in range(iterations):
        started_at = time.perf_counter_ns()
        operation()
        elapsed_ns = time.perf_counter_ns() - started_at
        durations_ms.append(elapsed_ns / 1_000_000)

    return Measurement(
        name=name,
        runs=iterations,
        minimum_ms=min(durations_ms),
        average_ms=statistics.fmean(durations_ms),
        median_ms=statistics.median(durations_ms),
        p95_ms=percentile(durations_ms, 0.95),
        maximum_ms=max(durations_ms),
    )


def ensure_expected_total(
    actual_total: int,
    expected_total: int,
) -> None:
    if actual_total != expected_total:
        raise RuntimeError(
            "Benchmark sırasında test kayıt sayısı değişti: "
            f"beklenen={expected_total}, gerçek={actual_total}."
        )


def benchmark_database_lists(
    db: Session,
    *,
    run_id: str,
    total: int,
    page_size: int,
    iterations: int,
) -> list[Measurement]:
    repository = SQLAlchemyProductRepository(db)
    marker = marker_for(run_id)
    last_offset = max(0, total - page_size)
    scenarios = [
        ("db.list.id.asc.first_page", "id", "asc", 0),
        ("db.list.id.asc.last_page", "id", "asc", last_offset),
        ("db.list.name.asc", "name", "asc", 0),
        ("db.list.name.desc", "name", "desc", 0),
        ("db.list.price.desc", "price", "desc", 0),
        ("db.list.stock.asc", "stock", "asc", 0),
    ]
    measurements = []

    for name, sort_by, sort_order, offset in scenarios:
        def operation(
            sort_by=sort_by,
            sort_order=sort_order,
            offset=offset,
        ):
            db.expire_all()
            items, actual_total = repository.get_all(
                owner_public_id=None,
                search=marker,
                sort_by=sort_by,
                sort_order=sort_order,
                offset=offset,
                limit=page_size,
            )
            ensure_expected_total(actual_total, total)

            if not items:
                raise RuntimeError(
                    f"{name} sorgusu ürün döndürmedi."
                )

        measurements.append(
            measure(
                name,
                operation,
                iterations=iterations,
            )
        )

    return measurements


def get_sample_public_id(
    db: Session,
    run_id: str,
) -> str:
    marker = marker_for(run_id)
    public_id = db.execute(
        select(ProductModel.public_id)
        .where(ProductModel.name.like(f"{marker}%"))
        .order_by(ProductModel.id.asc())
        .limit(1)
    ).scalar_one_or_none()

    if public_id is None:
        raise RuntimeError(
            f"{run_id} için örnek ürün bulunamadı."
        )

    return public_id


def benchmark_database_detail(
    db: Session,
    *,
    public_id: str,
    iterations: int,
) -> tuple[Measurement, object]:
    repository = SQLAlchemyProductRepository(db)

    def operation():
        db.expire_all()
        product = repository.get_by_public_id(
            public_id=public_id,
            owner_id=None,
        )

        if product is None:
            raise RuntimeError("DB örnek ürünü döndürmedi.")

        return product

    measurement = measure(
        "db.detail.by_public_id",
        operation,
        iterations=iterations,
    )

    return measurement, operation()


def redis_is_available() -> tuple[bool, str | None]:
    try:
        redis_client.ping()
        return True, None
    except RedisError as error:
        return False, str(error)


def benchmark_cache(
    *,
    product,
    iterations: int,
) -> list[Measurement]:
    cache = RedisProductCacheRepository()
    missing_public_id = str(uuid.uuid4())
    cache.invalidate(missing_public_id)
    cache.set(product)

    if cache.get(product.public_id) is None:
        raise RuntimeError(
            "Redis cache doğrulaması başarısız oldu."
        )

    def cache_hit():
        cached_product = cache.get(product.public_id)

        if cached_product is None:
            raise RuntimeError(
                "Benchmark sırasında beklenen cache kaydı bulunamadı."
            )

    def cache_miss():
        if cache.get(missing_public_id) is not None:
            raise RuntimeError(
                "Cache miss anahtarı beklenmedik veri döndürdü."
            )

    def cache_set():
        cache.set(product)

    measurements = [
        measure(
            "redis.detail.hit",
            cache_hit,
            iterations=iterations,
        ),
        measure(
            "redis.detail.miss",
            cache_miss,
            iterations=iterations,
        ),
        measure(
            "redis.detail.set",
            cache_set,
            iterations=iterations,
        ),
    ]
    cache.invalidate(missing_public_id)

    return measurements


def print_measurements(measurements: list[Measurement]) -> None:
    headers = (
        "Ölçüm",
        "Tekrar",
        "Min ms",
        "Ort ms",
        "P50 ms",
        "P95 ms",
        "Max ms",
    )
    rows = [
        (
            item.name,
            str(item.runs),
            f"{item.minimum_ms:.3f}",
            f"{item.average_ms:.3f}",
            f"{item.median_ms:.3f}",
            f"{item.p95_ms:.3f}",
            f"{item.maximum_ms:.3f}",
        )
        for item in measurements
    ]
    widths = [
        max(len(row[index]) for row in [headers, *rows])
        for index in range(len(headers))
    ]

    def format_row(row):
        return "  ".join(
            value.ljust(widths[index])
            for index, value in enumerate(row)
        )

    print(format_row(headers))
    print(format_row(tuple("-" * width for width in widths)))

    for row in rows:
        print(format_row(row))


def run_benchmark(
    db: Session,
    *,
    run_id: str,
    page_size: int,
    list_iterations: int,
    detail_iterations: int,
    cache_iterations: int,
) -> None:
    if not 1 <= page_size <= 100:
        raise ValueError("page_size 1 ile 100 arasında olmalıdır.")

    total = count_products(db, run_id)

    if total == 0:
        raise RuntimeError(
            f"{run_id} run_id için test verisi bulunamadı."
        )

    print(
        f"\nBenchmark: run_id={run_id}, kayıt={total}, "
        f"db={engine.dialect.name}"
    )

    measurements = benchmark_database_lists(
        db,
        run_id=run_id,
        total=total,
        page_size=page_size,
        iterations=list_iterations,
    )
    sample_public_id = get_sample_public_id(db, run_id)
    detail_measurement, sample_product = benchmark_database_detail(
        db,
        public_id=sample_public_id,
        iterations=detail_iterations,
    )
    measurements.append(detail_measurement)

    cache_available, cache_error = redis_is_available()

    if cache_available:
        measurements.extend(
            benchmark_cache(
                product=sample_product,
                iterations=cache_iterations,
            )
        )
    else:
        print(
            "Redis ölçümleri atlandı; bağlantı kurulamadı: "
            f"{cache_error}"
        )

    print_measurements(measurements)
    print(
        "\nNot: Bunlar tek süreçte repository/cache seviyesinde "
        "sıcak ölçümlerdir; HTTP, auth ve ağ gecikmesi dahil değildir."
    )


def invalidate_cache_keys(public_ids: list[str]) -> tuple[int, str | None]:
    available, error = redis_is_available()

    if not available:
        return 0, error

    deleted = 0

    try:
        for public_id_chunk in chunked(public_ids):
            keys = [
                RedisProductCacheRepository._key(public_id)
                for public_id in public_id_chunk
            ]
            deleted += redis_client.delete(*keys)
    except RedisError as redis_error:
        return deleted, str(redis_error)

    return deleted, None


def cleanup_products(
    db: Session,
    *,
    run_id: str,
) -> tuple[int, int, str | None]:
    marker = marker_for(run_id)
    product_filter = ProductModel.name.like(f"{marker}%")
    product_ids = select(ProductModel.id).where(product_filter)
    product_public_ids = select(ProductModel.public_id).where(
        product_filter
    )
    public_ids = list(
        db.execute(product_public_ids).scalars().all()
    )

    if not public_ids:
        return 0, 0, None

    try:
        db.execute(
            delete(product_tags).where(
                product_tags.c.product_id.in_(product_ids)
            )
        )
        db.execute(
            delete(ProductDetailModel).where(
                ProductDetailModel.product_id.in_(product_ids)
            )
        )
        db.execute(
            delete(ActivityLogModel).where(
                ActivityLogModel.entity_type == "PRODUCT",
                ActivityLogModel.entity_id.in_(product_public_ids),
            )
        )
        result = db.execute(
            delete(ProductModel).where(product_filter)
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    cache_deleted, cache_error = invalidate_cache_keys(public_ids)
    return result.rowcount or 0, cache_deleted, cache_error


def add_common_benchmark_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--list-iterations", type=int, default=10)
    parser.add_argument("--detail-iterations", type=int, default=100)
    parser.add_argument("--cache-iterations", type=int, default=500)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Ürün DB/cache performans testi için güvenli dummy veri aracı."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed_parser = subparsers.add_parser(
        "seed",
        help="İşaretli dummy ürünler ekler.",
    )
    seed_parser.add_argument("--run-id", default=None)
    seed_parser.add_argument("--count", type=int, default=DEFAULT_COUNT)
    seed_parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
    )
    seed_parser.add_argument("--owner-email", default=None)

    benchmark_parser = subparsers.add_parser(
        "benchmark",
        help="Mevcut bir test veri setini ölçer.",
    )
    add_common_benchmark_arguments(benchmark_parser)

    cleanup_parser = subparsers.add_parser(
        "cleanup",
        help="Yalnızca verilen run_id test verilerini siler.",
    )
    cleanup_parser.add_argument("--run-id", required=True)

    run_parser = subparsers.add_parser(
        "run",
        help="Seed, benchmark ve varsayılan olarak cleanup çalıştırır.",
    )
    run_parser.add_argument("--run-id", default=None)
    run_parser.add_argument("--count", type=int, default=DEFAULT_COUNT)
    run_parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
    )
    run_parser.add_argument("--owner-email", default=None)
    run_parser.add_argument("--page-size", type=int, default=100)
    run_parser.add_argument("--list-iterations", type=int, default=10)
    run_parser.add_argument("--detail-iterations", type=int, default=100)
    run_parser.add_argument("--cache-iterations", type=int, default=500)
    run_parser.add_argument(
        "--keep-data",
        action="store_true",
        help="Benchmark sonrasında dummy verileri silmez.",
    )

    return parser


def print_cleanup_result(
    run_id: str,
    deleted: int,
    cache_deleted: int,
    cache_error: str | None,
) -> None:
    print(
        f"Cleanup tamamlandı: run_id={run_id}, "
        f"db_silinen={deleted}, cache_silinen={cache_deleted}"
    )

    if cache_error is not None:
        print(
            "Cache cleanup atlandı veya kısmen tamamlandı: "
            f"{cache_error}"
        )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    db = SessionLocal()

    try:
        if args.command == "seed":
            run_id = args.run_id or create_run_id()
            inserted, elapsed, owner_email = seed_products(
                db,
                run_id=run_id,
                count=args.count,
                batch_size=args.batch_size,
                owner_email=args.owner_email,
            )
            print(
                f"Seed tamamlandı: run_id={run_id}, kayıt={inserted}, "
                f"süre={elapsed:.3f}s, owner={owner_email}"
            )
            print(
                "Test: DEBUG=false python "
                "scripts/product_performance.py benchmark "
                f"--run-id {run_id}"
            )
            print(
                "Sil: DEBUG=false python "
                "scripts/product_performance.py cleanup "
                f"--run-id {run_id}"
            )
            return 0

        if args.command == "benchmark":
            run_benchmark(
                db,
                run_id=args.run_id,
                page_size=args.page_size,
                list_iterations=args.list_iterations,
                detail_iterations=args.detail_iterations,
                cache_iterations=args.cache_iterations,
            )
            return 0

        if args.command == "cleanup":
            deleted, cache_deleted, cache_error = cleanup_products(
                db,
                run_id=args.run_id,
            )
            print_cleanup_result(
                args.run_id,
                deleted,
                cache_deleted,
                cache_error,
            )
            return 0

        run_id = args.run_id or create_run_id()
        seed_completed = False

        try:
            inserted, elapsed, owner_email = seed_products(
                db,
                run_id=run_id,
                count=args.count,
                batch_size=args.batch_size,
                owner_email=args.owner_email,
            )
            seed_completed = True
            print(
                f"Seed tamamlandı: run_id={run_id}, kayıt={inserted}, "
                f"süre={elapsed:.3f}s, owner={owner_email}"
            )
            run_benchmark(
                db,
                run_id=run_id,
                page_size=args.page_size,
                list_iterations=args.list_iterations,
                detail_iterations=args.detail_iterations,
                cache_iterations=args.cache_iterations,
            )
        finally:
            if not args.keep_data and seed_completed:
                deleted, cache_deleted, cache_error = cleanup_products(
                    db,
                    run_id=run_id,
                )
                print_cleanup_result(
                    run_id,
                    deleted,
                    cache_deleted,
                    cache_error,
                )

        if args.keep_data:
            print(
                "Dummy veriler korundu. Silmek için: "
                "DEBUG=false python "
                "scripts/product_performance.py cleanup "
                f"--run-id {run_id}"
            )

        return 0
    except (RuntimeError, ValueError) as error:
        print(f"Hata: {error}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
