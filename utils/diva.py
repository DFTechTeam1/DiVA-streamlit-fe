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
        query_image: int,
        prediction_label: Optional[list] = None,
    ) -> tuple[dict, int]:
        self.payload.encoded_image = encoded_image
        self.payload.threshold = threshold
        self.payload.page = page
        self.payload.query_image = query_image
        self.payload.prediction_label = prediction_label
        async with httpx.AsyncClient() as client:
            logging.info("Proceeding request for image query.")

            response = await client.post(
                url=self.credentials.IMAGE_QUERY_API,
                json=self.payload.model_dump(),
                timeout=120,
            )

            data = response.json()

            return data, response.status_code
