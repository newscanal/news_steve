from __future__ import annotations
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, computed_field, PrivateAttr
from uuid import uuid4, UUID
from requests.exceptions import RequestException
import requests

class NewsOrder(BaseModel):
    """
    NewsOrder class for defining a news collection order.
    """
    _order_id: UUID = PrivateAttr(default_factory=uuid4)

    name: str = Field(..., description="Name of news company")
    rss: str = Field(..., description="Rss url of news order")
    categories: List[str] = Field(default_factory=list, description="Categories of news order")
    description: Optional[str] = Field(default=None, description="Description of news order")
    max_items: Optional[int] = Field(default=None, description="Maximum number of items to collect")

    @computed_field
    @property
    def order_id(self) -> UUID:
        return self._order_id
    
    @computed_field
    @property
    def order_key(self) -> str:
        return f"{self.name}_{'_'.join(self.categories)}" if self.categories else self.name
    
    @classmethod
    def from_dict(
        cls,
        data: Dict
    ) -> NewsOrder:
        """Create a NewsOrder from a dict"""
        return cls(**data)
    
    def check_rss(
        self,
        timeout: int = 5
    ) -> bool:
        """Check if the RSS URL is reachable and returns a 200 OK response."""
        if not self.rss or not self.rss.strip():
            return False
        try:
            response = requests.get(self.rss, timeout=timeout)
            return response.status_code == 200
        except RequestException:
            return False
        
    def order2dict(self) -> Dict:
        """NewsOrder to Dict"""
        return self.model_dump()
    
    def order2json(self, indent: int = 2) -> str:
        """NewsOrder to JSON"""
        return self.model_dump_json(indent=indent)
