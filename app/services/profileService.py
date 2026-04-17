
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple

from fastapi import HTTPException
from pydantic import ValidationError

from app.api.externalApis.agifyApi import AgifyAPI
from app.api.externalApis.genederizeApi import GenderizeAPI
from app.api.externalApis.nationalizeApi import NationalizeAPI
from app.data.models.profileDetails import CreateProfileInput, Profile
from app.data.respository.profileDatabase import get_profile_by_name, create_profile
from app.schemas.Responses.ProfileResponses import AgeGroup
from app.utils.classifyGroups import ProfileConverter
from config import AGE_BOUNDARIES

logger = logging.getLogger(__name__)


def generate_uuid_v7() -> str:

    try:
        uuid_str = str(uuid.uuid7())
        logger.debug(f"Generated UUID v7: {uuid_str}")
        return uuid_str
    except AttributeError:
        logger.error("uuid.uuid7() not available")
        raise RuntimeError("UUID v7 generation not available")


def get_utc_timestamp() -> str:

    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def classify_age_group(age: int) -> str:

    if age < 0 or age > 150:
        raise ValueError(f"Invalid age: {age}")

    for age_group, (min_age, max_age) in AGE_BOUNDARIES.items():
        if min_age <= age <= max_age:
            logger.debug(f"Age {age} classified as {age_group.value}")
            return age_group.value

    logger.warning(f"Age {age} could not be classified")
    return AgeGroup.SENIOR.value


async def validate_input_name(name: str) -> str:

    try:
        validated = CreateProfileInput(name=name)
        return validated.name
    except ValidationError as e:
        logger.warning(f"Input validation failed: {str(e)}")

        if "empty" in str(e).lower():
            raise HTTPException(status_code=400, detail="Missing or empty name")
        else:
            raise HTTPException(status_code=422, detail="Invalid type")
    except Exception as e:
        logger.error(f"Unexpected validation error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid request")


async def enrich_profile(name: str) -> Dict[str, Any]:

    logger.info(f"Starting profile enrichment for name: {name}")

    validated_name = await validate_input_name(name)

    try:
        logger.debug(f"Calling external APIs for name: {validated_name}")
        genderize_data = await GenderizeAPI.get_gender(validated_name)
        agify_data = await AgifyAPI.get_age(validated_name)
        nationalize_data = await NationalizeAPI.get_nationality(validated_name)

        age_group = classify_age_group(agify_data["age"])

        profile_dict = {
            "id": generate_uuid_v7(),
            "name": validated_name,
            "gender": genderize_data["gender"],
            "gender_probability": genderize_data["probability"],
            "sample_size": genderize_data["count"],
            "age": agify_data["age"],
            "age_group": age_group,
            "country_id": nationalize_data["country_id"],
            "country_probability": nationalize_data["probability"],
            "created_at": get_utc_timestamp()
        }

        try:
            profile_domain = Profile(**profile_dict)
            logger.info(f"Profile domain model validated: {profile_domain.id}")
            profile_data = ProfileConverter.to_dict(profile_domain)
        except ValidationError as e:
            logger.error(f"Profile domain validation failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Profile validation failed")

        logger.info(f"Profile enriched successfully for name: {validated_name} (ID: {profile_data['id']})")
        return profile_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during profile enrichment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Unexpected server error")


async def process_profile_creation(name: str) -> Tuple[Dict[str, Any], Optional[str]]:

    logger.info(f"Processing profile creation for name: {name}")

    validated_name = await validate_input_name(name)

    try:
        existing_profile = await get_profile_by_name(validated_name)

        if existing_profile:
            logger.info(f"Profile already exists for name: {validated_name}")
            return existing_profile, "Profile already exists"
    except Exception as e:
        logger.error(f"Error checking for existing profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected server error")

    logger.debug(f"Creating new profile for name: {validated_name}")
    profile_data = await enrich_profile(validated_name)

    try:
        await create_profile(profile_data)
        logger.info(f"New profile created successfully for name: {validated_name}")
        return profile_data, None
    except Exception as e:
        logger.error(f"Failed to create profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected server error")