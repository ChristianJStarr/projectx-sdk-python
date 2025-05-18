"""Base model implementations for ProjectX SDK."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """
    Base response model for all API responses.

    Contains common fields present in all ProjectX API responses.
    """

    success: bool = Field(..., description="Whether the request was successful")
    error_code: int = Field(0, alias="errorCode", description="Error code (0 = no error)")
    error_message: Optional[str] = Field(
        None, alias="errorMessage", description="Error message (if any)"
    )

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True
