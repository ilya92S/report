from pydantic import BaseModel, EmailStr, UUID4

class ReportRequest(BaseModel):
    full_name: str
    email: EmailStr
    UUID: UUID4 | None = None
    report_name: str
    inn: str

class ReportResponse(BaseModel):
    full_name: str
    email: EmailStr
    UUID: str
    report_name: str
    basic_info: dict
    contact_info: dict
    gov_purchases: dict
    taxes: dict
