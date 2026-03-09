from pydantic import BaseModel, ConfigDict


class PostCreate(BaseModel):
    """
    Schema for creating a post.
    """

    title: str
    content: str


class PostUpdate(BaseModel):
    """
    Schema for updating a post.
    """

    title: str | None = None
    content: str | None = None


class PostResponse(BaseModel):
    """
    Schema for returning a post in API responses.
    """

    id: int
    title: str
    content: str

    model_config = ConfigDict(from_attributes=True)