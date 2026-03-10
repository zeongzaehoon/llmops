import asyncio

from pydantic import BaseModel, Field
from typing import Optional

from utils.constants import *



class upsertPayload(BaseModel):
    index_name: str = Field(..., alias="index")
    id: str
    content: str
    metadata: dict

    class Config:
        populate_by_name = True


class searchPayload(BaseModel):
    index_name: str = Field(..., alias="index")
    query: str = Field(..., alias="search")
    filter: Optional[str] = None
    k: Optional[int] = 4

    class Config:
        populate_by_name = True


class deleteIdPayload(BaseModel):
    id: str
    index_name: str = Field(..., alias="index")
    
    class Config:
        populate_by_name = True


class deleteFilterPayload(BaseModel):
    filter: dict
    index_name: str = Field(..., alias="index")
    
    class Config:
        populate_by_name = True