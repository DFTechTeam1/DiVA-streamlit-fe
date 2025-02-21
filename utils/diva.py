import httpx
from typing import Optional
from utils.logger import logging
from src.secret import Config
from src.schema import ImageQuery

class DiVAConnector:
    def __init__(self):
        self.credentials = Config()
        
    async def grab_similar(
        self,
        encoded_image: str,
        threshold: float,
        page: int,
        image_per_page: int,
        prediction_label: Optional[list] = None
    ) -> Optional[dict]:
        body = ImageQuery(
            encoded_image=encoded_image,
            threshold=threshold,
            page=page,
            image_per_page=image_per_page,
            prediction_label=prediction_label
        )
        
        async with httpx.AsyncClient() as client:
            try:
                logging.info(f"Proceeding request to {self.credentials.IMAGE_QUERY_API}")
                response = await client.post(url=self.credentials.IMAGE_QUERY_API, json=body.model_dump())
                data = response.json()
                
                
                if not data.get("success"):
                    error_detail = data.get("detail", {})
                    logging.error(f"Error whlile communicate with API: {error_detail}.")
                    raise Exception("Internal Server Error")
                else:
                    logging.info(f"Success searching similar image.")
                
                return data
                    
            except Exception as e:
                logging.error(f"Error while communicate with API: {e}.")
                raise Exception("Internal Server Error")
            finally:
                await client.aclose()
            
            return None