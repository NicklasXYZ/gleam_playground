from pydantic import BaseModel

class BaseSnippet(BaseModel):
    code: str

class Snippet(BaseSnippet):
    snippetID: str

    class Config:
        orm_mode = True
