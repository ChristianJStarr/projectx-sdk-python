"""Data models for contract-related API responses."""

from typing import List

from pydantic import BaseModel, Field, model_validator

from projectx_sdk.models.base import BaseResponse


class Contract(BaseModel):
    """
    Contract (instrument) data model.

    Represents a tradable financial instrument in the ProjectX platform.
    """

    id: str = Field(..., description="The unique contract identifier")
    name: str = Field(..., description="The human-readable name/symbol of the contract")
    description: str = Field(..., description="A descriptive title for the contract")
    tick_size: float = Field(
        ..., alias="tickSize", description="The minimum price increment for the contract"
    )
    tick_value: float = Field(..., alias="tickValue", description="The monetary value of one tick")
    active_contract: bool = Field(
        ...,
        alias="activeContract",
        description="Whether this is the active contract (e.g., front-month)",
    )

    class Config:
        """Pydantic model configuration."""

        populate_by_name = True  # Support both snake_case and camelCase


class ContractSearchResponse(BaseResponse):
    """
    Response model for contract search operations.

    Contains a list of contracts matching the search criteria.
    """

    contracts: List[Contract] = Field(
        default_factory=list, description="List of matching contracts"
    )
