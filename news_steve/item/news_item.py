from __future__ import annotations
from typing import Optional, Dict
from pydantic import BaseModel, Field, computed_field, PrivateAttr
from uuid import uuid4, UUID
from bs4 import BeautifulSoup
import time
import requests

from news_steve.order import NewsOrder

class NewsItem(BaseModel):
    """
    NewsItem class for a news info.
    """
    _item_id: UUID = PrivateAttr(default_factory=uuid4)

    news_order: Optional[NewsOrder] = Field(default=None, description="NewsOrder that is source NewsItem.")
    title: str = Field(..., description="Title of NewsItem.")
    link: str = Field(..., description="Link of NewsItem.")
    published: Optional[str] = Field(default=None, description="(String)Published time of NewsItem.")
    published_parsed: Optional[time.struct_time] = Field(default=None, description="(time.struct_time)Published time of NewsItem.")
    author: Optional[str] = Field(default=None, description="Author of NewsItem.")
    category: Optional[str] = Field(default=None, description="Category of NewsItem.")
    summary: Optional[str] = Field(default=None, description="Summary of NewsItem.")

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {
            BeautifulSoup: lambda v: str(v),
            time.struct_time: lambda v: time.strftime("%Y-%m-%d %H:%M:%S", v)
        }
    }

    @computed_field
    @property
    def item_id(self) -> UUID:
        return self._item_id
    
    @computed_field
    @property
    def html(self) -> Optional[str]:
        """
        Returns the HTML of the NewsItem URL link.
        If request fails or link is None, return None.
        """
        if not self.link:
            return None
        
        try:
            response = requests.get(self.link, timeout=5)
            response.raise_for_status()
            return response.text
        except Exception:
            return None
        
    @computed_field
    @property
    def soup(self) -> Optional[BeautifulSoup]:
        """
        Returns the BeautifulSoup of the newsItem URL link.
        If request fails or link is None, return None.
        """
        html = self.html
        if not html:
            return None
        return BeautifulSoup(html, "html.parser")
    
    def print(self) -> None:
        """
        Print NewsItem fields.
        """
        print(f"\n{self.__class__.__name__} Fields")
        for field, value in self.model_dump().items():
            print(f"- {field}: {value}")
    
    def get_order(self) -> Optional[Dict]:
        """
        Returns source NewsOrder (to dict) of NewsItem.
        If NewsOrder is None, return None.
        """
        if not self.news_order:
            return None
        return self.news_order.order2dict()

    def to_dict(self) -> Dict:
        """NewsItem to Dict"""
        return self.model_dump()
    
    def to_json(self, indent: int = 2) -> str:
        """NewsItem to JSON"""
        return self.model_dump_json(indent=indent)
