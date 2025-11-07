# models/order_operations.py
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict


class AcceptOrderInput(BaseModel):
    """Input for accepting an order."""
    order_id: str = Field(..., description="The order ID to accept", examples=["L6y8nffb2tz22ZTKq"])


class DeclineOrderInput(BaseModel):
    """Input for declining an order."""
    order_id: str = Field(..., description="The order ID to decline", examples=["L6y8nffb2tz22ZTKq"])
    decline_reason: Optional[str] = Field(None, description="Reason for declining", examples=["Incomplete documentation"])


class SubmitOrderInput(BaseModel):
    """Input for submitting an order."""
    order_id: str = Field(..., description="The order ID to submit", examples=["L6y8nffb2tz22ZTKq"])


class MessageInput(BaseModel):
    """Input for sending a message."""
    order_id: str = Field(..., description="The order ID to send message to", examples=["L6y8nffb2tz22ZTKq"])
    text: str = Field(..., description="The message text", examples=["Please provide additional information"])
    attachments: Optional[List[str]] = Field(None, description="List of attachment IDs", examples=[["file_id_1", "file_id_2"]])


class SendMessageResponse(BaseModel):
    """Response from send message mutation."""
    success: Optional[bool] = None


class FileData(BaseModel):
    """File data for adding files."""
    name: str = Field(..., description="File name", examples=["base64doc"])
    base_64: str = Field(..., description="Base64 encoded file content", examples=["VGhpcyBpcyBhIGRvY3VtZW50IHN1Ym1pdHRlZCBvdmVyIFF1YWxpYSBNYXJrZXRwbGFjZSBBUEkgaW4gYmFzZTY0IGVuY29kaW5nLg=="])
    is_primary: Optional[bool] = Field(None, description="Whether this is a primary document", examples=[True])


class AddFilesInput(BaseModel):
    """Input for adding files to an order."""
    order_id: str = Field(..., description="The order ID to add files to", examples=["K5EnbsZjHnut3yhLk"])
    files: FileData = Field(..., description="File data with name, base64 content, and is_primary flag")


class AddFilesResponse(BaseModel):
    """Response from add files mutation."""
    outstanding_tasks: Optional[List[str]] = None


class RemoveFilesInput(BaseModel):
    """Input for removing files from an order."""
    order_id: str = Field(..., description="The order ID to remove files from", examples=["K5EnbsZjHnut3yhLk"])
    file_ids: List[str] = Field(..., description="List of file IDs to remove", examples=[["file_id_1", "file_id_2"]])


class RemoveFilesResponse(BaseModel):
    """Response from remove files mutation."""
    order: Optional[Dict[str, Any]] = None
    outstanding_tasks: Optional[List[str]] = None


# Title Search Models

class SeniorLien(BaseModel):
    """Senior lien data."""
    recorded_date: Optional[str] = Field(None, examples=["2025-11-08"])
    instrument_number: Optional[str] = Field(None, examples=["233"])
    book: Optional[str] = Field(None, examples=["12"])
    page: Optional[str] = Field(None, examples=["1"])


class Subordination(BaseModel):
    """Subordination data."""
    recorded_date: Optional[str] = Field(None, examples=["2025-11-08"])
    instrument_number: Optional[str] = Field(None, examples=["654"])
    book: Optional[str] = Field(None, examples=["456"])
    page: Optional[str] = Field(None, examples=["44"])
    senior_lien: Optional[SeniorLien] = None


class Assignment(BaseModel):
    """Assignment data."""
    assignee: Optional[str] = Field(None, examples=["assignee"])
    recorded_date: Optional[str] = Field(None, examples=["2021-02-02"])
    instrument_number: Optional[str] = Field(None, examples=["234"])
    book: Optional[str] = Field(None, examples=["234"])
    page: Optional[str] = Field(None, examples=["23"])


class Encumbrance(BaseModel):
    """Encumbrance data."""
    type: Optional[str] = Field(None, examples=["MORTGAGE_LIEN"])
    lender: Optional[str] = Field(None, examples=["Big Red Bank"])
    amount: Optional[str] = Field(None, examples=["4323.22"])
    certificate_of_title_number: Optional[str] = Field(None, examples=["345"])
    mortgage_date: Optional[str] = Field(None, examples=["2022-01-01"])
    mortgagor: Optional[str] = Field(None, examples=["Big Red Bank"])
    deed_of_trust_date: Optional[str] = Field(None, examples=["2022-01-02"])
    trustor: Optional[str] = Field(None, examples=["trustor"])
    trustee: Optional[str] = Field(None, examples=["trustee"])
    assignments: Optional[Assignment] = None
    subordinations: Optional[Subordination] = None
    recorded_date: Optional[str] = Field(None, examples=["2025-11-09"])
    instrument_number: Optional[str] = Field(None, examples=["22"])
    book: Optional[str] = Field(None, examples=["23"])
    page: Optional[str] = Field(None, examples=["4322"])
    document_number: Optional[str] = Field(None, examples=["2"])


class Deed(BaseModel):
    """Deed data."""
    grantor: Optional[str] = Field(None, examples=["grantor"])
    grantee: Optional[str] = Field(None, examples=["grantee"])
    deed_date: Optional[str] = Field(None, examples=["2025-11-10"])
    recorded_date: Optional[str] = Field(None, examples=["2025-11-06"])
    instrument_number: Optional[str] = Field(None, examples=["234"])
    book: Optional[str] = Field(None, examples=["34"])
    page: Optional[str] = Field(None, examples=["23"])
    certificate_of_title_number: Optional[str] = Field(None, examples=["234234"])
    document_number: Optional[str] = Field(None, examples=["g23"])


class PropertyData(BaseModel):
    """Property data for title search."""
    parcel_ids: Optional[str] = Field(None, examples=["23423kjh234"])
    legal_description: Optional[str] = Field(None, examples=["legal description"])
    estate_type: Optional[str] = Field(None, examples=["estateType"])
    title_vesting: Optional[str] = Field(None, examples=["Mr. and Mrs. Smith"])
    deeds: Optional[Deed] = None
    encumbrances: Optional[Encumbrance] = None


class AdditionalCost(BaseModel):
    """Additional cost item."""
    name: str = Field(..., examples=["Copies"])
    cost_per_unit: str = Field(..., examples=["0.50"])
    units: int = Field(..., examples=[4])
    is_discount: bool = Field(False, examples=[False])


class TemplateData(BaseModel):
    """Template data for requirements."""
    petitioner: Optional[str] = Field(None, examples=["Petitioner Field"])
    respondent: Optional[str] = Field(None, examples=["Respondent Field"])
    date: Optional[str] = Field(None, examples=["2022-01-01"])
    caseNumber: Optional[str] = Field(None, examples=["234234"])
    courtName: Optional[str] = Field(None, examples=["Matagorda County 120th"])


class TemplatedText(BaseModel):
    """Templated text for requirements."""
    template_string: Optional[str] = Field(None, examples=["Template String"])
    sub_types: Optional[List[str]] = Field(None, examples=[["subType1", "subType2"]])
    template_data: Optional[TemplateData] = None
    code: Optional[str] = Field(None, examples=["Divorce Decree"])


class ImproperMortgageLien(BaseModel):
    """Improper mortgage lien data."""
    lender: Optional[str] = Field(None, examples=["Lender Field"])
    mortgage_date: Optional[str] = Field(None, examples=["2025-11-06"])
    amount: Optional[str] = Field(None, examples=["35,456.00"])
    recorded_date: Optional[str] = Field(None, examples=["2025-11-06"])
    instrument_number: Optional[str] = Field(None, examples=["234"])
    book: Optional[str] = Field(None, examples=["23"])
    page: Optional[str] = Field(None, examples=["1"])
    hyperlink: Optional[str] = Field(None, examples=["www.qualia.com"])


class Requirement(BaseModel):
    """Requirement item - flexible to handle different types."""
    type: str = Field(..., examples=["templatedText"])
    indent: Optional[bool] = Field(None, examples=[False])
    text: Optional[str] = Field(None, examples=["Terms and provisions of a Decree of Divorce..."])
    templatedText: Optional[TemplatedText] = None
    improperMortgageLien: Optional[ImproperMortgageLien] = None


class TitleSearchForm(BaseModel):
    """Form data for title search."""
    properties: Optional[PropertyData] = None
    search_completed_date: Optional[str] = Field(None, examples=["2025-11-10"])
    search_completed_time: Optional[str] = Field(None, examples=["10:10AM"])
    requirements: Optional[List[Requirement]] = None
    exceptions: Optional[List[Dict[str, Any]]] = Field(None, examples=[[]])
    additional_costs: Optional[AdditionalCost] = None
    always_charge_additional_costs: Optional[bool] = Field(None, examples=[True])


class FulfillTitleSearchInput(BaseModel):
    """Input for fulfilling title search."""
    order_id: str = Field(..., description="The order ID to fulfill", examples=["K5EnbsZjHnut3yhLk"])
    form: TitleSearchForm = Field(..., description="Title search form data")


class FulfillTitleSearchInputWrapper(BaseModel):
    """Wrapper for fulfill title search input (matches GraphQL format)."""
    input: FulfillTitleSearchInput


class FulfillTitleSearchResponse(BaseModel):
    """Response from fulfill title search mutation."""
    outstanding_tasks: Optional[List[str]] = None
