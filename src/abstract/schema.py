"""Base DTO schemas."""

from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class BaseDTO(BaseModel):
    """Base DTO with a common configuration for all business DTOs.

    Provides:
    - ORM mode for SQLAlchemy entity conversion
    - Validation on assignment
    - Support for both field names and aliases
    """

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )


class EntityDTO(BaseDTO):
    """DTO with id field, maps entity pk to id."""

    id: int = Field(alias="pk")


class TimestampDTO(BaseDTO):
    """DTO with timestamp fields."""

    created_at: datetime
    updated_at: datetime


class PaginatedResponse[T](BaseDTO):
    """Generic paginated response wrapper.

    Usage:
        ```python
        @router.get("/users", response_model=PaginatedResponse[UserDTO])
        async def list_users(limit: int = 20, offset: int = 0):
            users, total = await user_repo.paginate(limit=limit, offset=offset)
            return PaginatedResponse(
                items=users,
                total=total,
                limit=limit,
                offset=offset,
            )
        ```
    """

    items: list[T]
    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        """Check if there are more items beyond current page."""
        return self.offset + len(self.items) < self.total

    @property
    def page(self) -> int:
        """Current page number (1-indexed)."""
        if self.limit == 0:
            return 1
        return (self.offset // self.limit) + 1

    @property
    def total_pages(self) -> int:
        """Total number of pages."""
        if self.limit == 0:
            return 1
        return (self.total + self.limit - 1) // self.limit
