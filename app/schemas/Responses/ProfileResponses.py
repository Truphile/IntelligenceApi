from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class AgeGroup(str, Enum):
    CHILD = "child"
    TEENAGER = "teenager"
    ADULT = "adult"
    SENIOR = "senior"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class ProfileDataResponse(BaseModel):

    id: str = Field(..., description="UUID v7 identifier")
    name: str = Field(..., description="The enriched name")
    gender: str = Field(..., description="Predicted gender")
    gender_probability: float = Field(..., description="Gender confidence 0-1")
    sample_size: int = Field(..., description="Sample size for prediction")
    age: int = Field(..., description="Predicted age")
    age_group: str = Field(..., description="Age classification")
    country_id: str = Field(..., description="Country code")
    country_probability: float = Field(..., description="Country confidence 0-1")
    created_at: str = Field(..., description="UTC ISO 8601 timestamp")

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


class ProfileListItemResponse(BaseModel):
    """Simplified profile item for list responses - SPEC COMPLIANT"""
    id: str = Field(..., description="UUID v7 identifier")
    name: str = Field(..., description="Profile name")
    gender: str = Field(..., description="Predicted gender")
    age: int = Field(..., description="Predicted age")
    age_group: str = Field(..., description="Age classification")
    country_id: str = Field(..., description="Country code")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "id-1",
                "name": "emmanuel",
                "gender": "male",
                "age": 25,
                "age_group": "adult",
                "country_id": "NG"
            }
        }


class CreateProfileResponse(BaseModel):
    """Response for profile creation endpoint - SPEC COMPLIANT"""
    status: str = Field(..., description="Response status")
    message: Optional[str] = Field(None, description="Optional message (e.g., 'Profile already exists')")
    data: ProfileDataResponse = Field(..., description="Created profile data")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": None,
                "data": {
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
        }


class GetProfileResponse(BaseModel):

    status: str = Field(..., description="Response status")
    data: ProfileDataResponse = Field(..., description="Profile data")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "id": "b3f9c1e2-7d4a-4c91-9c2a-1f0a8e5b6d12",
                    "name": "emmanuel",
                    "gender": "male",
                    "gender_probability": 0.99,
                    "sample_size": 1234,
                    "age": 25,
                    "age_group": "adult",
                    "country_id": "NG",
                    "country_probability": 0.85,
                    "created_at": "2026-04-01T12:00:00Z"
                }
            }
        }


class ListProfilesResponse(BaseModel):

    status: str = Field(..., description="Response status")
    count: int = Field(..., description="Number of profiles returned")
    data: List[ProfileListItemResponse] = Field(..., description="List of profiles")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "count": 2,
                "data": [
                    {
                        "id": "id-1",
                        "name": "emmanuel",
                        "gender": "male",
                        "age": 25,
                        "age_group": "adult",
                        "country_id": "NG"
                    },
                    {
                        "id": "id-2",
                        "name": "sarah",
                        "gender": "female",
                        "age": 28,
                        "age_group": "adult",
                        "country_id": "US"
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):

    status: str = Field(..., description="Response status (always 'error')")
    message: str = Field(..., description="Error message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Profile not found"
            }
        }