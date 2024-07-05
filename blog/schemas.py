from pydantic import BaseModel


class Blog(BaseModel):
    title: str
    body: str


class ShowBlog(Blog):
    title: str
    body: str

    class Config:
        from_attributes = True



