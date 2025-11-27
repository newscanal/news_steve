from __future__ import annotations
from news_order import NewsOrder
from uuid import UUID
from typing import Union

class NewsOrderBundle(dict):
    """
    NewsOrderBundle class for bundling multiple NewsOrder object
    """
    def __setitem__(self, key: Union[NewsOrder, UUID], value: NewsOrder):
        if isinstance(key, NewsOrder):
            if not isinstance(value, NewsOrder):
                raise TypeError("Value must be a NewsOrder instance.")
            if key is not value:
                raise ValueError("Key and value must be the same NewsOrder instance.")
            super().__setitem__(key.order_id, value)
        elif isinstance(key, UUID):
            if not isinstance(value, NewsOrder):
                raise TypeError("Value must be a NewsOrder instance.")
            if key != value.order_id:
                raise ValueError("UUID key must match NewsOrder.order_id.")
            super().__setitem__(key, value)
        else:
            raise TypeError("Key must be a NewsOrder instance or UUID.")
        
    def __getitem__(self, key: Union[NewsOrder, UUID]):
        if isinstance(key, NewsOrder):
            return super().__getitem__(key.order_id)
        elif isinstance(key, UUID):
            return super().__getitem__(key)
        else:
            raise TypeError("Key must be a NewsOrder instance or UUID.")
    
    def __delitem__(self, key: Union[NewsOrder, UUID]):
        if isinstance(key, NewsOrder):
            super().__delitem__(key.order_id)
        elif isinstance(key, UUID):
            super().__delitem__(key)
        else:
            raise TypeError("Key must be a NewsOrder instance or UUID.")    
        
    def __contains__(self, key: Union[NewsOrder, UUID]):
        if isinstance(key, NewsOrder):
            return super().__contains__(key.order_id)
        elif isinstance(key, UUID):
            return super().__contains__(key)
        else:
            return False
         
    def tolist(self):
        """Return a list of NewsOrder instance"""
        return list(self.values())
    
    def get(self, order: NewsOrder, default=None):
        if not isinstance(order, NewsOrder):
            raise TypeError("Argument must be a NewsOrder instance.")
        return super().get(order.order_id, default)
    
    def get_by_id(self, id: UUID, default=None):
        return super().get(id, default)
    
    def get_by_name(self, name: str):
        """Return a list of NewsOrder instance that have same name"""
        return [order for order in self.values() if order.name == name]