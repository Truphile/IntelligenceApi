import os
from enum import Enum

from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
DEBUG = ENVIRONMENT == "development"

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", 10))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", 20))

GENDERIZE_API_URL = os.getenv("GENDERIZE_API_URL")
AGIFY_API_URL = os.getenv("AGIFY_API_URL")
NATIONALIZE_API_URL = os.getenv("NATIONALIZE_API_URL")
EXTERNAL_API_TIMEOUT = 10
EXTERNAL_API_MAX_RETRIES = 1

NAME_MIN_LENGTH = 1
NAME_MAX_LENGTH = 100

GENDER_CONFIDENCE_PROBABILITY = 0.7
GENDER_CONFIDENCE_SAMPLE_SIZE = 100

PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class AgeGroup(str, Enum):
    CHILD = "child"
    TEENAGER = "teenager"
    ADULT = "adult"
    SENIOR = "senior"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


AGE_BOUNDARIES = {
    AgeGroup.CHILD: (0, 12),
    AgeGroup.TEENAGER: (13, 19),
    AgeGroup.ADULT: (20, 59),
    AgeGroup.SENIOR: (60, 150),
}


def validate_config():

    import logging
    logger = logging.getLogger(__name__)

    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable not set")

    logger.info(f"✓ Configuration validated - Environment: {ENVIRONMENT}")