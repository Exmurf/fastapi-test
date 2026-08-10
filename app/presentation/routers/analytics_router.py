from datetime import datetime, time, date
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
)

from app.application.schemas.analytics_schema import (
    UserAnalyticsResponse,
)
from app.application.services.analytics_service import (
    AnalyticsService,
)
from app.domain.entities.user import User
from app.presentation.dependencies.analytics_dependencies import (
    get_analytics_service,
)
from app.presentation.dependencies.auth_dependencies import (
    get_current_user,
)
from app.presentation.responses import (
    ApiResponse,
    success_response,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)

@router.get(
    "/me",
    response_model=ApiResponse[
        UserAnalyticsResponse
    ],
)
def get_own_analytics(
    start_date: date | None = Query(
        default=None
    ),
    start_time: time | None = Query(
        default=None
    ),
    end_date: date | None = Query(
        default=None
    ),
    end_time: time | None = Query(
        default=None
    ),
    current_user: User = Depends(
        get_current_user
    ),
    service: AnalyticsService = Depends(
        get_analytics_service
    ),
):
    start_datetime = None

    if start_date is not None:
        start_datetime = datetime.combine(
            start_date,
            start_time or time.min,
        )

    end_datetime = None

    if end_date is not None:
        end_datetime = datetime.combine(
            end_date,
            end_time or time.max,
        )

    analytics = service.get_own_analytics(
        current_user=current_user,
        start_date=start_datetime,
        end_date=end_datetime,
    )

    return success_response(analytics)

@router.get(
    "/users/{user_public_id}",
    response_model=ApiResponse[
        UserAnalyticsResponse
    ],
)
def get_user_analytics(
    user_public_id: UUID,
    start_date: date | None = Query(
        default=None
    ),
    start_time: time | None = Query(
        default=None
    ),
    end_date: date | None = Query(
        default=None
    ),
    end_time: time | None = Query(
        default=None
    ),
    current_user: User = Depends(
        get_current_user
    ),
    service: AnalyticsService = Depends(
        get_analytics_service
    ),
):
    start_datetime = None

    if start_date is not None:
        start_datetime = datetime.combine(
            start_date,
            start_time or time.min,
        )

    end_datetime = None

    if end_date is not None:
        end_datetime = datetime.combine(
            end_date,
            end_time or time.max,
        )

    analytics = service.get_user_analytics(
        current_user=current_user,
        user_public_id=str(
            user_public_id
        ),
        start_date=start_datetime,
        end_date=end_datetime,
    )

    return success_response(analytics)