import httpx
from typing import Optional
from utils.logger import logging
from src.secret import QUERY_API
from src.schema import ImageQuery


class DiVAConnector:
    def __init__(self):
        self.payload = ImageQuery()

    async def grab_similar(
        self,
        filename: str,
        encoded_image: str,
        threshold: float,
        page: int,
        prediction: Optional[list] = None,
    ) -> tuple[dict, int]:
        self.payload.filename = filename
        self.payload.encoded_image = encoded_image
        self.payload.threshold = threshold
        self.payload.page = page
        self.payload.prediction = prediction

        try:
            async with httpx.AsyncClient() as client:
                logging.info("Proceeding request for image query.")

                response = await client.post(
                    url=QUERY_API,
                    json=self.payload.model_dump(),
                    timeout=180,
                )

                data = response.json()

                return data, response.status_code
        except httpx.ConnectError:
            raise Exception(
                "Unable to connect backend service. Please ensure backend server is ready."
            )
