from pydantic import BaseModel, Field, BeforeValidator
from typing import List, Annotated, Optional

PyObjectId = Annotated[str, BeforeValidator(str)]


class CategoryModel(BaseModel):
    id: Optional[PyObjectId] = Field(
        alias="_id", default=None, description="Category name as primary identifier"
    )
    name: str
    subCategories: List[str] = Field(default_factory=list)
