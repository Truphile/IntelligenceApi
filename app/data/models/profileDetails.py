
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum
from app.utils.classifyGroups import FilterValidator, ProfileValidator


class AgeGroupEnum(str, Enum):
    CHILD = "child"
    TEENAGER = "teenager"
    ADULT = "adult"
    SENIOR = "senior"


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"


class Profile(BaseModel):

    id: str = Field(..., description="UUID identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Profile name")
    gender: str = Field(..., description="Gender prediction")
    gender_probability: float = Field(..., ge=0.0, le=1.0, description="Gender confidence")
    sample_size: int = Field(..., ge=0, description="Sample size")
    age: int = Field(..., ge=0, le=150, description="Predicted age")
    age_group: str = Field(..., description="Age classification")
    country_id: str = Field(..., min_length=1, max_length=5, description="Country code")
    country_probability: float = Field(..., ge=0.0, le=1.0, description="Country confidence")
    created_at: str = Field(..., description="UTC ISO 8601 timestamp")

    @field_validator('name')
    @classmethod
    def validate_name(cls, value):
        return ProfileValidator.validate_name(value)

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, value):
        return ProfileValidator.validate_gender(value)

    @field_validator('age_group')
    @classmethod
    def validate_age_group(cls, value):
        return ProfileValidator.validate_age_group(value)

    @field_validator('created_at')
    @classmethod
    def validate_created_at(cls, value):
        return ProfileValidator.validate_created_at(value)

    @field_validator('country_id')
    @classmethod
    def validate_country_id(cls, value):
        return ProfileValidator.validate_country_id(value)

    @field_validator('gender_probability', 'country_probability')
    @classmethod
    def validate_probability(cls, value):
        return ProfileValidator.validate_probability(value)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "b3f9c1e2-7d4a-4c91-9c2a-1f0a8e5b6d12",
                "name": "ella",
                "gender": "female",
                "gender_probability": 0.99,
                "sample_size": 1234,
                "age": 46,
                "age_group": "adult",
                "country_id": "DRC",
                "country_probability": 0.85,
                "created_at": "2026-04-01T12:00:00Z"
            }
        }


class ProfileFilter(BaseModel):

    gender: Optional[str] = Field(None, description="Filter by gender")
    country_id: Optional[str] = Field(None, description="Filter by country code")
    age_group: Optional[str] = Field(None, description="Filter by age group")

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, value):
        return FilterValidator.validate_gender_filter(value)

    @field_validator('age_group')
    @classmethod
    def validate_age_group(cls, value):
        return FilterValidator.validate_age_group_filter(value)

    @field_validator('country_id')
    @classmethod
    def validate_country_id(cls, value):
        return FilterValidator.validate_country_filter(value)

    class Config:
        json_schema_extra = {
            "example": {
                "gender": "male",
                "country_id": "NG",
                "age_group": "adult"
            }
        }


class CreateProfileInput(BaseModel):

    name: str = Field(..., min_length=1, max_length=100, description="The name to enrich")

    @field_validator('name')
    @classmethod
    def validate_name(cls, value):
        return ProfileValidator.validate_name(value)

    class Config:
        json_schema_extra = {
            "example": {"name": "ella"}
        }