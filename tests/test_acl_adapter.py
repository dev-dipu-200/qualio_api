# tests/test_acl_adapter.py
import pytest
from services.acl_adapter import QualiaToInternalAdapter


class TestACLAdapter:
    """Tests for ACL adapter transformations."""

    def test_transform_complete_payload(self):
        """Test transformation with complete payload."""
        adapter = QualiaToInternalAdapter()
        qualia_data = {
            "order_number": "QO-123456",
            "vertical": "title",
            "product_type": "owner_policy",
            "customer_name": "ABC Title Company",
            "due_date": "2025-11-15",
            "properties": [
                {
                    "address_1": "123 Main St",
                    "city": "San Francisco",
                    "state": "CA",
                    "zipcode": "94102"
                }
            ]
        }

        result = adapter.transform(qualia_data)

        assert result["externalOrderId"] == "QO-123456"
        assert result["productCategory"] == "TITLE"
        assert result["productType"] == "owner_policy"
        assert result["source"] == "QUALIA_MARKETPLACE"
        assert result["dueDate"] == "2025-11-15"
        assert result["agency"]["agencyName"] == "ABC Title Company"
        assert result["state"]["stateCode"] == "CA"
        assert result["state"]["stateName"] == "California"
        assert len(result["properties"]) == 1
        assert result["properties"][0]["address"]["addressLine1"] == "123 Main St"

    def test_transform_filters_none_values(self):
        """Test that None values are filtered out."""
        adapter = QualiaToInternalAdapter()
        qualia_data = {
            "order_number": "QO-123456",
            "vertical": "title",
            "properties": [{"state": "TX"}]
        }

        result = adapter.transform(qualia_data)

        assert "externalOrderId" in result
        assert "productCategory" in result
        # productType should not be in result since it was None
        assert result.get("productType") is None

    def test_state_mapping_all_states(self):
        """Test state mapping for various US states."""
        adapter = QualiaToInternalAdapter()

        test_cases = [
            ("CA", "California"),
            ("TX", "Texas"),
            ("NY", "New York"),
            ("FL", "Florida"),
            ("WA", "Washington"),
            ("DC", "District of Columbia"),
            ("PR", "Puerto Rico"),
        ]

        for state_code, expected_name in test_cases:
            result = adapter._state_name(state_code)
            assert result == expected_name, f"Failed for {state_code}"

    def test_state_mapping_case_insensitive(self):
        """Test state mapping is case insensitive."""
        adapter = QualiaToInternalAdapter()

        assert adapter._state_name("ca") == "California"
        assert adapter._state_name("CA") == "California"
        assert adapter._state_name("Ca") == "California"

    def test_state_mapping_unknown_code(self):
        """Test state mapping with unknown code."""
        adapter = QualiaToInternalAdapter()

        result = adapter._state_name("XX")
        assert result == ""

    def test_state_mapping_empty_code(self):
        """Test state mapping with empty code."""
        adapter = QualiaToInternalAdapter()

        result = adapter._state_name(None)
        assert result == ""

        result = adapter._state_name("")
        assert result == ""

    def test_extract_properties_multiple(self):
        """Test extraction of multiple properties."""
        adapter = QualiaToInternalAdapter()
        qualia_data = {
            "properties": [
                {
                    "address_1": "123 Main St",
                    "city": "San Francisco",
                    "state": "CA",
                    "zipcode": "94102"
                },
                {
                    "address_1": "456 Oak Ave",
                    "city": "Los Angeles",
                    "state": "CA",
                    "zipcode": "90001"
                }
            ]
        }

        result = adapter._extract_properties(qualia_data)

        assert len(result) == 2
        assert result[0]["address"]["addressLine1"] == "123 Main St"
        assert result[0]["address"]["city"] == "San Francisco"
        assert result[1]["address"]["addressLine1"] == "456 Oak Ave"
        assert result[1]["address"]["city"] == "Los Angeles"

    def test_extract_properties_empty(self):
        """Test extraction with no properties."""
        adapter = QualiaToInternalAdapter()
        qualia_data = {"properties": []}

        result = adapter._extract_properties(qualia_data)

        assert result == []

    def test_extract_state_from_first_property(self):
        """Test state extraction uses first property."""
        adapter = QualiaToInternalAdapter()
        qualia_data = {
            "properties": [
                {"state": "CA"},
                {"state": "TX"}  # Should be ignored
            ]
        }

        result = adapter._extract_state(qualia_data)

        assert result["stateCode"] == "CA"
        assert result["stateName"] == "California"

    def test_transform_uppercase_vertical(self):
        """Test that vertical is uppercased."""
        adapter = QualiaToInternalAdapter()
        qualia_data = {
            "order_number": "QO-123",
            "vertical": "title",
            "properties": [{"state": "CA"}]
        }

        result = adapter.transform(qualia_data)

        assert result["productCategory"] == "TITLE"

    def test_transform_empty_vertical(self):
        """Test transformation with empty vertical."""
        adapter = QualiaToInternalAdapter()
        qualia_data = {
            "order_number": "QO-123",
            "vertical": "",
            "properties": [{"state": "CA"}]
        }

        result = adapter.transform(qualia_data)

        assert result["productCategory"] == ""

    def test_all_50_states_mapped(self):
        """Verify all 50 states plus territories are in mapping."""
        adapter = QualiaToInternalAdapter()

        expected_states = [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
            "DC", "PR", "VI", "GU", "AS"
        ]

        for state_code in expected_states:
            result = adapter._state_name(state_code)
            assert result != "", f"State {state_code} not mapped"
            assert len(result) > 2, f"State {state_code} has invalid name"
