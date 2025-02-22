from pydantic import BaseModel, Field
from typing import Optional


class ImageQuery(BaseModel):
    encoded_image: str = None
    threshold: float = Field(default=None, ge=0.1, le=1.0)
    page: int = Field(default=None, ge=1)
    image_per_page: int = Field(default=None, ge=1)
    prediction_label: Optional[list] = None
