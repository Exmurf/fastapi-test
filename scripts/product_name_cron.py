from datetime import datetime, timedelta
from pathlib import Path
import sqlite3


CRON_INTERVAL_MINUTES = 10

SOURCE_TEXT = "test"
TARGET_TEXT = "demo"


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database.db"


def update_product_names() -> None:
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        now = datetime.now()

        interval_start = (
            now - timedelta(minutes=CRON_INTERVAL_MINUTES)
        )

        products = cursor.execute(
            """
            SELECT id, name
            FROM products
            WHERE updated_at >= ?
            """,
            (
                interval_start.strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                ),
            ),
        ).fetchall()

        updated_count = 0

        for product_id, name in products:
            if SOURCE_TEXT not in name:
                continue

            new_name = name.replace(
                SOURCE_TEXT,
                TARGET_TEXT,
            )

            cursor.execute(
                """
                UPDATE products
                SET name = ?
                WHERE id = ?
                """,
                (
                    new_name,
                    product_id,
                ),
            )

            updated_count += 1

        connection.commit()

        print(
            f"{datetime.now()} - "
            f"{updated_count} product guncellendi"
        )

    finally:
        connection.close()


if __name__ == "__main__":
    update_product_names()