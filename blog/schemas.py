from pydantic import BaseModel
from fastapi import Form


class Blog(BaseModel):
    title: str
    body: str

    def as_form(
        cls, title: str = Form(...), body: str=Form(...),
    ):
        return cls(title=title, body=body)






