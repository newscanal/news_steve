from typing import Dict, List, DefaultDict
from uuid import UUID
from collections import defaultdict
from sortedcontainers import SortedDict, SortedSet
from news_steve.item import NewsItem

def meta_updater(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self._update_meta()
        return result
    return wrapper

class NewsContainer:
    """
    NewsContainer class for a multiple NewsItems and querying and managing them.
    """
    def __init__(self):
        self._container: Dict[UUID, NewsItem] = dict()
        self._meta: Dict = dict()

        self._index_by_category: DefaultDict[str, SortedSet[UUID]] = defaultdict(lambda: SortedSet(key=lambda uid: self._container[uid].published))
        self._index_by_order: DefaultDict[str, SortedSet[UUID]] = defaultdict(lambda: SortedSet(key=lambda uid: self._container[uid].published))
        self._index_by_date: SortedDict[str, UUID] = SortedDict()
        
    def _update_meta(self):
        self._meta['total_items'] = len(self)
        self._meta['num_of_items_per_category'] = {k: len(v) for k,v in self._index_by_category.items()}
        self._meta['num_of_items_per_order'] = {k: len(v) for k,v in self._index_by_order.items()}

    @property
    def categories(self) -> List[str]:
        return list(self._index_by_category.keys())
    
    @property
    def orders(self) -> List[str]:
        return list(self._index_by_order.keys())
    
    @property
    def meta(self) -> Dict[str, int]:
        return self._meta
    
    def __len__(self):
        return len(self._container)