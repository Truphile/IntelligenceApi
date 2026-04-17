import httpx
import logging
from typing import Dict, Any
from fastapi import HTTPException

from config import GENDERIZE_API_URL, EXTERNAL_API_TIMEOUT

logger = logging.getLogger(__name__)


class GenderizeAPI:

    URL = GENDERIZE_API_URL

    @staticmethod
    async def get_gender(name: str) -> Dict[str, Any]:

        try:
            logger.debug(f"Calling Genderize API for name: {name}")

            async with httpx.AsyncClient(timeout=EXTERNAL_API_TIMEOUT) as client:
                response = await client.get(GenderizeAPI.URL, params={"name": name})
                response.raise_for_status()
                data = response.json()

                logger.debug(f"Genderize response: {data}")

                if data.get("gender") is None or data.get("count", 0) == 0:
                    logger.warning(
                        f"Invalid Genderize response: gender={data.get('gender')}, count={data.get('count')}")
                    raise HTTPException(
                        status_code=502,
                        detail="Genderize returned an invalid response"
                    )

                return {
                    "gender": data["gender"],
                    "probability": data.get("probability", 0),
                    "count": data.get("count", 0)
                }

        except httpx.HTTPError as e:
            logger.error(f"Genderize HTTP error: {str(e)}")
            raise HTTPException(status_code=502, detail="Genderize returned an invalid response")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Genderize unexpected error: {str(e)}")
            raise HTTPException(status_code=502, detail="Genderize returned an invalid response")