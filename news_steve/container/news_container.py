from typing import Dict, List, Set, Optional, DefaultDict, Union
from uuid import UUID
from collections import defaultdict
from sortedcontainers import SortedDict, SortedSet
from news_steve.item import NewsItem
from news_steve.order import NewsOrder

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

        self._index_by_category: DefaultDict[str, set[UUID]] = defaultdict(set)
        self._index_by_order: DefaultDict[str, set[UUID]] = defaultdict(set)
        self._index_by_date: SortedDict[str, SortedSet[UUID]] = SortedDict()
        
    def _update_meta(self):
        self._meta['total_items'] = len(self)
        self._meta['per_category'] = {k: len(v) for k,v in self._index_by_category.items()}
        self._meta['per_order'] = {k: len(v) for k,v in self._index_by_order.items()}

    @property
    def categories(self) -> List[str]:
        return list(self._index_by_category.keys())
    
    @property
    def orders(self) -> List[str]:
        return list(self._index_by_order.keys())
    
    @property
    def meta(self) -> Dict[str, int]:
        return self._meta
    
    def get_all_itmes(self, sort: bool = False, revsere: bool = False):
        if (sort):
            return sorted(self._container.values(), key=lambda x:x.published, reverse=reversed)
        return self._container.values()
    
    def __len__(self):
        return len(self._container)
    
    def _add(self, item: NewsItem):
        if not isinstance(item, NewsItem):
            raise ValueError(f"NewsContainer can only add NewsItems. This input is {type(item)}.")
        id = item.item_id
        self._container[id] = item

        category = "None" if item.category is None else item.category
        order = "None" if item.news_order is None else item.news_order.order_id
        date = "None" if item.published is None else item.published

        if category != "None":
            self._index_by_category[category].add(id)

        if order != "None":
            self._index_by_order[order].add(id)
        
        if date != "None":
            if date not in self._index_by_date:
                self._index_by_date[date] = SortedSet()
            self._index_by_date[date].add(id)       
        
    @meta_updater
    def add(self, items: Union[NewsItem, List[NewsItem]]):
        """
        Add method that process a NewsItem or multiple NewsItmes.
        """
        if isinstance(items, NewsItem):
            items = [items]

        for item in items:
            self._add(item)

    def _remove(self, item: NewsItem):
        if not isinstance(item, NewsItem):
            raise ValueError(f"NewsContainer can only remove NewsItems. This input is {type(item)}")
                
        id = item.item_id
        if id not in self._container:
            return
        
        category = "None" if item.category is None else item.category
        order = "None" if item.news_order is None else item.news_order.order_id
        date = "None" if item.published is None else item.published

        if category != "None" and category in self._index_by_category:
            self._index_by_category[category].discard(id)
            if not self._index_by_category[category]:
                del self._index_by_category[category]

        if order != "None" and order in self._index_by_order:
            self._index_by_order[order].discard(id)
            if not self._index_by_order[order]:
                del self._index_by_order[order]

        if date != "None" and date in self._index_by_date:
            self._index_by_date[date].discard(id)
            if not self._index_by_date[date]:
                del self._index_by_date[date]

        del self._container[id]
    
    @meta_updater
    def remove(self, items: Union[NewsItem, List[NewsItem]]):
        """
        Remove method that process a NewsItem or multiple NewsItmes.
        """
        if isinstance(items, NewsItem):
            items = [items]

        for item in items:
            self._remove(item)        

    def _get(self, key: UUID) -> NewsItem:
        if key not in self._container:
            raise KeyError(f"NewsItem with id {key} not found in NewsContainer.")
        return self._container[key]
    
    def get(self, key: Union[str, UUID, List[UUID]]) -> List[NewsItem]:
        """
        Get method that process a NewsItem or multiple NewsItmes.
        """
        single = False
        if isinstance(key, (UUID, str)):
            key = [UUID(key) if isinstance(key, str) else key]
            single=True

        result = [self._get(k) for k in key]
        return result[0] if single else result
    
    def _search_category(self, category: str) -> Set[UUID]:
        if category not in self._index_by_category:
            raise ValueError(f"This category not in container. not valid category: {category}.")
        return self._index_by_category[category]

    def search_by_category(self, categories: Union[str, List[str]], sort=False, reverse=False) -> List[NewsItem]:
        """
        Search NewsItems by a category or multiple category
        """
        if isinstance(categories, str):
            categories = [categories]

        id_set = set()
        for category in categories:
            id_set.update(self._search_category(category))

        result = [self._container[id_] for id_ in id_set]

        if sort:
            return sorted(result, key=lambda x: x.published, reverse=reverse)
        return result


    def _search_order(self, order:str) -> Set[UUID]:
        if order not in self._index_by_order:
            raise ValueError(f"This order not in container. not valid order: {order}.")
        return self._index_by_order[order]

    def serach_by_order(self, orders: Union[str, NewsOrder, List[str], List[NewsOrder]], sort=False, reverse=False) -> List[NewsItem]:
        """
        Search NewsItems by a NewsOrder or multiple NewsOrder
        """
        if isinstance(orders, (str, NewsOrder)):
            orders = [orders]

        id_set = set()
        for order in orders:
            if isinstance(order, NewsOrder):
                key = order.order_id
            else:
                key = order
            id_set.update(self._search_order(key))
        
        result = [self._container[id_] for id_ in id_set]

        if sort:
            return sorted(result, key=lambda x: x.published, reverse=reverse)
        return result

    def serach_by_date(self, start: str, end: Optional[str] = None, reverse=False):
        """
        Search NewsItems by start time and end time.
        if end time is None, only start time NewsItems search.
        """
        if end is None:
            end = start

        keys = self._index_by_date.keys()

        result = []
        for date in keys.irange(start, end):
            for id_ in self._index_by_date[date]:
                result.append(self._container[id_])

        if reverse:
            return result.reverse()
        return result

    ## TODO Serialization/Deserialization