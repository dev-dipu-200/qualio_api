# services/acl_adapter.py
import logging

logger = logging.getLogger(__name__)

class QualiaToInternalAdapter:
    """Adapter to transform Qualia data format to internal API format."""

    # Comprehensive US state mapping
    STATE_NAMES = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
        "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
        "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
        "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
        "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
        "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
        "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
        "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
        "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
        "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
        "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
        "PR": "Puerto Rico", "VI": "Virgin Islands", "GU": "Guam", "AS": "American Samoa"
    }

    FIELD_MAPPING = {
        'order_id': 'externalOrderId',
        'vertical': 'productCategory',
        'product_type': 'productType',
        'property_address': 'propertyAddress',
    }

    def transform(self, qualia_data: dict) -> dict:
        """Transform Qualia order data to internal API format."""
        logger.debug(f"Transforming Qualia data with order_number: {qualia_data.get('order_number')}")

        internal = {
            "externalOrderId": qualia_data.get("order_number"),
            "productCategory": qualia_data.get("vertical", "").upper(),
            "productType": qualia_data.get("product_type"),
            "source": "QUALIA_MARKETPLACE",
            "state": self._extract_state(qualia_data),
            "properties": self._extract_properties(qualia_data),
            "agency": {"agencyName": qualia_data.get("customer_name", "")},
            "dueDate": qualia_data.get("due_date"),
            "notes": ""
        }
        # Filter out None values
        result = {k: v for k, v in internal.items() if v is not None}
        logger.debug(f"Transformed data fields: {list(result.keys())}")
        return result

    def _extract_state(self, data):
        """Extract state information from property data."""
        addr = data.get("properties", [{}])[0]
        state_code = addr.get("state")
        return {
            "stateCode": state_code,
            "stateName": self._state_name(state_code)
        }

    def _extract_properties(self, data):
        """Extract and format property addresses."""
        props = data.get("properties", [])
        return [{
            "address": {
                "addressLine1": p.get("address_1"),
                "city": p.get("city"),
                "state": p.get("state"),
                "zip": p.get("zipcode")
            }
        } for p in props]

    def _state_name(self, code):
        """Get full state name from state code."""
        if not code:
            return ""
        state_name = self.STATE_NAMES.get(code.upper(), "")
        if not state_name:
            logger.warning(f"Unknown state code: {code}")
        return state_name