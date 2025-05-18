"""Base model implementations for ProjectX SDK."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field


class BaseModel(ABC):
    """
    Base class for API data models.

    All specific API model classes inherit from this base class.
    """

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]):
        """
        Create a model instance from a dictionary (typically API response data).

        Args:
            data (dict): Dictionary containing model data

        Returns:
            BaseModel: An instance of the model
        """
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to a dictionary for API requests.

        Returns:
            dict: Dictionary representation of the model
        """
        pass


class BaseResponse(PydanticBaseModel):
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
