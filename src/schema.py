from pydantic import BaseModel, Field
from typing import Optional


class ImageQuery(BaseModel):
    encoded_image: Optional[str] = None
    threshold: float = Field(default=0.3, ge=0.1, le=1.0)
    page: int = Field(default=1, ge=1)
    query_image: int = Field(default=50, ge=50, le=200)
    prediction_label: Optional[list] = None
