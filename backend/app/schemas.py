from pydantic import BaseModel

class CrossRequest(BaseModel):
    n: int
    k: int
    z: int = 7

class RSDPGRequest(BaseModel):
    n: int
    k: int
    m: int
    z: int = 127
    p: int = 509