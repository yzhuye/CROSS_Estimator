from pydantic import BaseModel

class CrossRequest(BaseModel):
    n: int
    k: int