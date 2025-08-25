from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CategoryPydantic(BaseModel):
    id: int
    category_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
