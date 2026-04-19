from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse
from typing import Optional
import logging

from app.data.repository.profileDatabase import get_profiles, delete_profile, get_profile_by_id
from app.schemas.Requests.ProfileRequests import CreateProfileRequest
from app.schemas.Responses.ProfileResponses import CreateProfileResponse, ProfileDataResponse, ListProfilesResponse, \
    GetProfileResponse, ProfileListItemResponse
from app.services.profileService import process_profile_creation

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/profiles",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Profile created successfully"},
        200: {"description": "Profile already exists (idempotent)"},
        400: {"description": "Missing or empty name"},
        422: {"description": "Invalid name format"},
        502: {"description": "External API failed"},
        500: {"description": "Server error"}
    }
)
async def create_profile(request: CreateProfileRequest):

    logger.info(f"POST /api/profiles - Creating profile for name: {request.name}")

    try:
        profile_data, message = await process_profile_creation(request.name)

        response_status = status.HTTP_200_OK if message else status.HTTP_201_CREATED

        response_data = CreateProfileResponse(
            status="success",
            message=message,
            data=ProfileDataResponse(**profile_data)
        )

        logger.info(f"Profile creation result: status={response_status}, message={message}")

        return JSONResponse(
            status_code=response_status,
            content=response_data.model_dump(exclude_none=False)
        )

    except HTTPException as e:
        logger.warning(f"HTTPException in create_profile: {e.status_code} - {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content={"status": "error", "message": e.detail}
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_profile: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": "Unexpected server error"}
        )


@router.get(
    "/profiles/{profile_id}",
    response_model=GetProfileResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Profile found"},
        404: {"description": "Profile not found"},
        500: {"description": "Server error"}
    }
)
async def get_profile(profile_id: str):

    logger.info(f"GET /api/profiles/{profile_id}")

    try:
        profile = await get_profile_by_id(profile_id)

        if not profile:
            logger.warning(f"Profile not found: {profile_id}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": "Profile not found"}
            )

        logger.info(f"Profile retrieved: {profile_id}")
        return GetProfileResponse(
            status="success",
            data=ProfileDataResponse(**profile)
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_profile: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": "Unexpected server error"}
        )


@router.get(
    "/profiles",
    response_model=ListProfilesResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of profiles"},
        500: {"description": "Server error"}
    }
)
async def list_profiles(
        gender: Optional[str] = Query(None, description="Filter by gender"),
        country_id: Optional[str] = Query(None, description="Filter by country ID"),
        age_group: Optional[str] = Query(None, description="Filter by age group")
) -> ListProfilesResponse:

    logger.info(f"GET /api/profiles - Filters: gender={gender}, country_id={country_id}, age_group={age_group}")

    try:
        profiles = await get_profiles(gender=gender, country_id=country_id, age_group=age_group)

        profile_items = [
            ProfileListItemResponse(
                id=p["id"],
                name=p["name"],
                gender=p["gender"],
                age=p["age"],
                age_group=p["age_group"],
                country_id=p["country_id"]
            )
            for p in profiles
        ]

        logger.info(f"Retrieved {len(profile_items)} profiles")

        return ListProfilesResponse(
            status="success",
            count=len(profile_items),
            data=profile_items
        )

    except Exception as e:
        logger.error(f"Unexpected error in list_profiles: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": "Unexpected server error"}
        )


@router.delete(
    "/profiles/{profile_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Profile deleted successfully"},
        404: {"description": "Profile not found"},
        500: {"description": "Server error"}
    }
)
async def delete_profile_endpoint(profile_id: str):

    logger.info(f"DELETE /api/profiles/{profile_id}")

    try:
        deleted = await delete_profile(profile_id)

        if not deleted:
            logger.warning(f"Profile not found for deletion: {profile_id}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": "Profile not found"}
            )

        logger.info(f"Profile deleted successfully: {profile_id}")
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )

    except Exception as e:
        logger.error(f"Unexpected error in delete_profile: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": "Unexpected server error"}
        )