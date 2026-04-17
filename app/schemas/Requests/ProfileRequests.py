from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CreateProfileRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="The name to enrich (alphabetic characters and spaces only)"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, value):
        if not value or not value.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        return value.strip()

    class Config:
        json_schema_extra = {
            "example": {"name": "ella"}
        }


class GetProfilesFilterRequest(BaseModel):

    gender: Optional[str] = Field(None, description="Filter by gender (male, female)")
    country_id: Optional[str] = Field(None, description="Filter by country code")
    age_group: Optional[str] = Field(None, description="Filter by age group")

    class Config:
        json_schema_extra = {
            "example": {
                "gender": "male",
                "country_id": "NG",
                "age_group": "adult"
            }
        }