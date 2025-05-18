"""Tests for validator functions."""

import pytest
from pydantic import BaseModel

from projectx_sdk.utils.validators import (
    ValidationError,
    validate_contract_id_format,
    validate_int_range,
    validate_model,
    validate_not_none,
    validate_string_not_empty,
)


class TestValidators:
    """Tests for the validation utilities."""

    def test_validate_not_none(self):
        """Test validating non-None values."""
        # Test with non-None values
        assert validate_not_none(42, "value") == 42
        assert validate_not_none("test", "value") == "test"
        assert validate_not_none([], "value") == []

        # Test with None value
        with pytest.raises(ValueError) as excinfo:
            validate_not_none(None, "value")
        assert "value must not be None" in str(excinfo.value)

    def test_validate_int_range(self):
        """Test validating integer ranges."""
        # Test within range
        assert validate_int_range(5, "value", 0, 10) == 5
        assert validate_int_range(0, "value", 0, 10) == 0
        assert validate_int_range(10, "value", 0, 10) == 10

        # Test without min/max
        assert validate_int_range(5, "value") == 5
        assert validate_int_range(5, "value", min_value=0) == 5
        assert validate_int_range(5, "value", max_value=10) == 5

        # Test below min
        with pytest.raises(ValueError) as excinfo:
            validate_int_range(-1, "value", 0, 10)
        assert "value must be at least 0" in str(excinfo.value)

        # Test above max
        with pytest.raises(ValueError) as excinfo:
            validate_int_range(11, "value", 0, 10)
        assert "value must be at most 10" in str(excinfo.value)

        # Test with None
        with pytest.raises(ValueError) as excinfo:
            validate_int_range(None, "value", 0, 10)  # type: ignore
        assert "value cannot be None" in str(excinfo.value)

    def test_validate_string_not_empty(self):
        """Test validating non-empty strings."""
        # Test with non-empty strings
        assert validate_string_not_empty("test", "value") == "test"
        assert validate_string_not_empty("a", "value") == "a"

        # Test with empty string
        with pytest.raises(ValueError) as excinfo:
            validate_string_not_empty("", "value")
        assert "value must not be empty" in str(excinfo.value)

        # Test with None
        with pytest.raises(ValueError) as excinfo:
            validate_string_not_empty(None, "value")
        assert "value must not be None" in str(excinfo.value)

    def test_validate_contract_id_format(self):
        """Test validating contract ID format."""
        # Test with valid contract IDs
        assert validate_contract_id_format("CON.F.US.ENQ.H25") == "CON.F.US.ENQ.H25"
        assert validate_contract_id_format("CON.O.US.AAPL.C150") == "CON.O.US.AAPL.C150"
        assert validate_contract_id_format("CON.F.US.ES.Z24") == "CON.F.US.ES.Z24"

        # Test with invalid contract IDs
        with pytest.raises(ValueError) as excinfo:
            validate_contract_id_format("invalid")
        assert "Invalid contract ID format" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            validate_contract_id_format("CON.F.USA.ENQ.H25")  # 3 chars in region
        assert "Invalid contract ID format" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            validate_contract_id_format("con.f.us.enq.h25")  # lowercase
        assert "Invalid contract ID format" in str(excinfo.value)

        # Test with empty string
        with pytest.raises(ValueError) as excinfo:
            validate_contract_id_format("")
        assert "must not be empty" in str(excinfo.value)

        # Test with None
        with pytest.raises(ValueError) as excinfo:
            validate_contract_id_format(None)  # type: ignore
        assert "Contract ID cannot be None or empty" in str(excinfo.value)

    def test_validate_model(self):
        """Test validating model conversion."""
        # Create a test model
        class TestModel(BaseModel):
            id: int
            name: str

        # Test with valid data
        data = {"id": 1, "name": "test"}
        model = validate_model(data, TestModel)
        assert isinstance(model, TestModel)
        assert model.id == 1
        assert model.name == "test"

        # Test with invalid data
        with pytest.raises(ValueError) as excinfo:
            validate_model({"id": "not an int", "name": "test"}, TestModel)
        assert "Invalid TestModel data" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            validate_model({"id": 1}, TestModel)  # Missing name
        assert "Invalid TestModel data" in str(excinfo.value)

    def test_validate_contract_id_format_invalid_none(self):
        """Test validating a None contract ID."""
        with pytest.raises(ValidationError) as excinfo:
            # Explicitly cast None to string for mypy
            validate_contract_id_format(None)  # type: ignore

        assert "Contract ID cannot be None or empty" in str(excinfo.value)

    def test_validate_int_range_none(self):
        """Test validating a None value for int range."""
        with pytest.raises(ValidationError) as excinfo:
            # Explicitly cast None to int for mypy
            validate_int_range(None, "test_field", 1, 10)  # type: ignore

        assert "test_field cannot be None" in str(excinfo.value)
