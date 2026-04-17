import re
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ProfileValidator:
    @staticmethod
    def validate_name(value: str) -> str:

        if not value or not value.strip():
            raise ValueError("Name cannot be empty")

        if not re.match(r"^[a-zA-Z\s]+$", value.strip()):
            raise ValueError("Name must contain only alphabetic characters and spaces")

        logger.debug(f"Name validated: {value}")
        return value.strip()

    @staticmethod
    def validate_gender(value: str) -> str:

        if value.lower() not in ["male", "female"]:
            raise ValueError("Gender must be 'male' or 'female'")

        logger.debug(f"Gender validated: {value}")
        return value.lower()

    @staticmethod
    def validate_age_group(value: str) -> str:

        allowed = ["child", "teenager", "adult", "senior"]

        if value.lower() not in allowed:
            raise ValueError(f"Age group must be one of: {', '.join(allowed)}")

        logger.debug(f"Age group validated: {value}")
        return value.lower()

    @staticmethod
    def validate_created_at(value: str) -> str:

        if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", value):
            raise ValueError("created_at must be in ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ")

        logger.debug(f"Timestamp validated: {value}")
        return value

    @staticmethod
    def validate_country_id(value: str) -> str:

        if not value.replace("-", "").isalpha():
            raise ValueError("Country ID must contain only alphabetic characters")

        logger.debug(f"Country ID validated: {value}")
        return value.upper()

    @staticmethod
    def validate_probability(value: float) -> float:

        if not (0.0 <= value <= 1.0):
            raise ValueError("Probability must be between 0.0 and 1.0")

        logger.debug(f"Probability validated: {value}")
        return value


class ProfileConverter:

    @staticmethod
    def to_dict(model: Any) -> Dict[str, Any]:

        try:
            result = model.model_dump()
            logger.debug(f"Model converted to dictionary with {len(result)} fields")
            return result
        except Exception as e:
            logger.error(f"Failed to convert model to dictionary: {str(e)}")
            raise

    @staticmethod
    def to_dict_exclude_none(model: Any) -> Dict[str, Any]:

        try:
            result = model.model_dump(exclude_none=True)
            logger.debug(f"Model converted to dictionary (excluding None) with {len(result)} fields")
            return result
        except Exception as e:
            logger.error(f"Failed to convert model: {str(e)}")
            raise

    @staticmethod
    def to_json(model: Any) -> str:

        try:
            result = model.model_dump_json()
            logger.debug("Model converted to JSON")
            return result
        except Exception as e:
            logger.error(f"Failed to convert model to JSON: {str(e)}")
            raise


class FilterValidator:

    @staticmethod
    def validate_gender_filter(value: str) -> str:

        if value is not None and value.lower() not in ["male", "female"]:
            raise ValueError("Gender filter must be 'male' or 'female'")

        logger.debug(f"Gender filter validated: {value}")
        return value.lower() if value else None

    @staticmethod
    def validate_age_group_filter(value: str) -> str:

        allowed = ["child", "teenager", "adult", "senior"]

        if value is not None and value.lower() not in allowed:
            raise ValueError(f"Age group filter must be one of: {', '.join(allowed)}")

        logger.debug(f"Age group filter validated: {value}")
        return value.lower() if value else None

    @staticmethod
    def validate_country_filter(value: str) -> str:

        if value is not None and not value.replace("-", "").isalpha():
            raise ValueError("Country filter must contain only alphabetic characters")

        logger.debug(f"Country filter validated: {value}")
        return value.upper() if value else None