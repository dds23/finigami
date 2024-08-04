from pydantic import BaseModel
from typing import List, Optional


class URLInput(BaseModel):
    url: str


class URLListInput(BaseModel):
    urls: List


class ResultOutput(BaseModel):
    info: Optional[str] = 'URL already processed, showing saved result'
    title: str
    summary: str
    links: List
