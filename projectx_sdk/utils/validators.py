"""Validation utilities for the ProjectX SDK."""

import re
from typing import Any, Dict, Optional, Type, TypeVar


class ValidationError(ValueError):
    """Exception raised for validation errors in the ProjectX SDK."""

    pass


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
        ValidationError: If the value is None
    """
    if value is None:
        raise ValidationError(f"{name} must not be None")
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
        ValidationError: If the value is outside the specified range
    """
    if value is None:
        raise ValidationError(f"{name} cannot be None")

    if min_value is not None and value < min_value:
        raise ValidationError(f"{name} must be at least {min_value}")

    if max_value is not None and value > max_value:
        raise ValidationError(f"{name} must be at most {max_value}")

    return value


def validate_non_negative(value: int, name: str) -> int:
    """
    Validate that an integer is non-negative (>= 0).

    Args:
        value: The integer to validate
        name: The name of the parameter (for error message)

    Returns:
        The validated integer

    Raises:
        ValidationError: If the value is negative
    """
    return validate_int_range(value, name, min_value=0)


def validate_string_not_empty(value: Optional[str], name: str) -> str:
    """
    Validate that a string is not empty.

    Args:
        value: The string to validate
        name: The name of the parameter (for error message)

    Returns:
        The validated string

    Raises:
        ValidationError: If the string is None or empty
    """
    validate_not_none(value, name)

    if not value:
        raise ValidationError(f"{name} must not be empty")

    return value


def validate_contract_id_format(contract_id: str) -> str:
    """
    Validate that a contract ID has the correct format.

    Args:
        contract_id: The contract ID to validate

    Returns:
        The validated contract ID

    Raises:
        ValidationError: If the contract ID has an invalid format
    """
    if contract_id is None:
        raise ValidationError("Contract ID cannot be None or empty")

    if not contract_id:
        raise ValidationError("contract_id must not be empty")

    # Example pattern for contract IDs: "CON.F.US.EP.H24"
    pattern = r"^CON\.[A-Z]\.[A-Z]{2}\.[A-Z0-9]{1,5}\.[A-Z0-9]{1,5}$"

    if not re.match(pattern, contract_id):
        raise ValidationError(
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
        ValidationError: If the dictionary cannot be converted to the model
    """
    try:
        # Try model_validate (Pydantic v2) first, then parse_obj (Pydantic v1)
        if hasattr(model_class, "model_validate"):
            result: T = model_class.model_validate(value)  # type: ignore
            return result
        else:
            result: T = model_class.parse_obj(value)  # type: ignore
            return result
    except Exception as e:
        raise ValidationError(f"Invalid {model_class.__name__} data: {e}")
