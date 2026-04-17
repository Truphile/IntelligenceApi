import httpx
import logging
from typing import Dict, Any
from fastapi import HTTPException

from config import NATIONALIZE_API_URL, EXTERNAL_API_TIMEOUT

logger = logging.getLogger(__name__)


class NationalizeAPI:

    URL = NATIONALIZE_API_URL

    @staticmethod
    async def get_nationality(name: str) -> Dict[str, Any]:

        try:
            logger.debug(f"Calling Nationalize API for name: {name}")

            async with httpx.AsyncClient(timeout=EXTERNAL_API_TIMEOUT) as client:
                response = await client.get(NationalizeAPI.URL, params={"name": name})
                response.raise_for_status()
                data = response.json()

                logger.debug(f"Nationalize response: {data}")

                countries = data.get("country", [])
                if not countries or len(countries) == 0:
                    logger.warning(f"Invalid Nationalize response: no country data")
                    raise HTTPException(status_code=502, detail="Nationalize returned an invalid response")

                top_country = max(countries, key=lambda x: x.get("probability", 0))

                return {
                    "country_id": top_country.get("country_id", ""),
                    "probability": top_country.get("probability", 0)
                }

        except httpx.HTTPError as e:
            logger.error(f"Nationalize HTTP error: {str(e)}")
            raise HTTPException(status_code=502, detail="Nationalize returned an invalid response")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Nationalize unexpected error: {str(e)}")
            raise HTTPException(status_code=502, detail="Nationalize returned an invalid response")