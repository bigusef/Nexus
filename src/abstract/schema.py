"""Base DTO schemas"""

from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class BaseDTO(BaseModel):
    """
    Base DTO with common fields for all business DTOs.

    Provides:
    - Timestamp fields (created_at, updated_at)
    - Pydantic configuration for ORM mode
    """

    model_config = ConfigDict(
        from_attributes=True,  # Pydantic v2 (was orm_mode=True in v1)
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,  # Allow both field name and alias
    )


class EntityDTO(BaseDTO):
    """DTO with id fields, maps entity pk to id"""

    id: int = Field(alias="pk")


class TimestampDTO(BaseDTO):
    """DTO with timestamp fields"""

    created_at: datetime
    updated_at: datetime
