import httpx
import logging
from typing import Dict, Any
from fastapi import HTTPException

from config import AGIFY_API_URL, EXTERNAL_API_TIMEOUT

logger = logging.getLogger(__name__)


class AgifyAPI:

    URL = AGIFY_API_URL

    @staticmethod
    async def get_age(name: str) -> Dict[str, Any]:

        try:
            logger.debug(f"Calling Agify API for name: {name}")

            async with httpx.AsyncClient(timeout=EXTERNAL_API_TIMEOUT) as client:
                response = await client.get(AgifyAPI.URL, params={"name": name})
                response.raise_for_status()
                data = response.json()

                logger.debug(f"Agify response: {data}")

                if data.get("age") is None:
                    logger.warning(f"Invalid Agify response: age is null")
                    raise HTTPException(status_code=502, detail="Agify returned an invalid response")

                return {"age": data["age"], "count": data.get("count", 0)}

        except httpx.HTTPError as e:
            logger.error(f"Agify HTTP error: {str(e)}")
            raise HTTPException(status_code=502, detail="Agify returned an invalid response")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Agify unexpected error: {str(e)}")
            raise HTTPException(status_code=502, detail="Agify returned an invalid response")