import httpx
from typing import Optional
from utils.logger import logging
from src.secret import Config
from src.schema import ImageQuery


class DiVAConnector:
    def __init__(self):
        self.credentials = Config()
        self.payload = ImageQuery()

    async def grab_similar(
        self,
        encoded_image: str,
        threshold: float,
        page: int,
        prediction_label: Optional[list] = None,
    ) -> Optional[dict]:
        self.payload.encoded_image = encoded_image
        self.payload.threshold = threshold
        self.payload.page = page
        self.payload.prediction_label = prediction_label

        async with httpx.AsyncClient() as client:
            try:
                logging.info("Proceeding request for image query.")

                response = await client.post(
                    url=self.credentials.IMAGE_QUERY_API,
                    json=self.payload.model_dump(),
                    timeout=120,
                )
                response.raise_for_status()

                data = response.json()

                if not data.get("success"):
                    error_detail = data.get("detail", {})
                    logging.error(
                        f"Error while communicating with API: {error_detail}."
                    )
                    raise Exception("Internal Server Error")
                else:
                    logging.info("Success searching similar image.")

                return data

            except httpx.HTTPStatusError as e:
                logging.error(
                    f"HTTP error: {e.response.status_code} - {e.response.text}"
                )
                raise Exception("Internal Server Error")
            except httpx.RequestError as e:
                logging.error(f"Request error: {str(e)}")
                raise Exception("Internal Server Error")
            except Exception as e:
                logging.error(f"Unexpected error: {str(e)}")
                raise Exception("Internal Server Error")

        return None
