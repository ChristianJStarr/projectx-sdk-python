"""Validation utilities for the ProjectX SDK."""

import re
from typing import Any, Dict, Optional, Type, TypeVar

T = TypeVar("T")


def validate_not_none(value: Optional[Any], name: str) -> Any:
    """
    Validate that a value is not None.

    Args:
        value: The value to validate
        name: The name of the parameter (for error message)

    Returns:
        The validated value

    Raises:
        ValueError: If the value is None
    """
    if value is None:
        raise ValueError(f"{name} must not be None")
    return value


def validate_int_range(
    value: int, name: str, min_value: Optional[int] = None, max_value: Optional[int] = None
) -> int:
    """
    Validate that an integer is within a range.

    Args:
        value: The integer to validate
        name: The name of the parameter (for error message)
        min_value: The minimum allowed value (inclusive)
        max_value: The maximum allowed value (inclusive)

    Returns:
        The validated integer

    Raises:
        ValueError: If the value is outside the specified range
    """
    validate_not_none(value, name)

    if min_value is not None and value < min_value:
        raise ValueError(f"{name} must be at least {min_value}")

    if max_value is not None and value > max_value:
        raise ValueError(f"{name} must be at most {max_value}")

    return value


def validate_string_not_empty(value: Optional[str], name: str) -> str:
    """
    Validate that a string is not empty.

    Args:
        value: The string to validate
        name: The name of the parameter (for error message)

    Returns:
        The validated string

    Raises:
        ValueError: If the string is None or empty
    """
    validate_not_none(value, name)

    if not value:
        raise ValueError(f"{name} must not be empty")

    return value


def validate_contract_id_format(contract_id: str) -> str:
    """
    Validate that a contract ID has the correct format.

    Args:
        contract_id: The contract ID to validate

    Returns:
        The validated contract ID

    Raises:
        ValueError: If the contract ID has an invalid format
    """
    validate_string_not_empty(contract_id, "contract_id")

    # Example pattern for contract IDs: "CON.F.US.EP.H24"
    pattern = r"^CON\.[A-Z]\.[A-Z]{2}\.[A-Z0-9]{1,5}\.[A-Z0-9]{1,5}$"

    if not re.match(pattern, contract_id):
        raise ValueError(
            f"Invalid contract ID format: {contract_id}. "
            "Expected format: CON.<type>.<region>.<symbol>.<month/year>"
        )

    return contract_id


def validate_model(value: Dict[str, Any], model_class: Type[T]) -> T:
    """
    Validate that a dictionary can be converted to a model.

    Args:
        value: The dictionary to validate
        model_class: The model class to convert to

    Returns:
        An instance of the model

    Raises:
        ValueError: If the dictionary cannot be converted to the model
    """
    try:
        return model_class.model_validate(value)
    except Exception as e:
        raise ValueError(f"Invalid {model_class.__name__} data: {e}")
