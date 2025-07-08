from .utils import request_json
from .urls import Urls, COUNTRY_USA


class Store(object):
    """The interface to the Store API

    You can use this to find store information about stores near an
    address, or to find the closest store to an address.
    
    Updated with flexible initialization and automatic data fetching.
    """
    
    def __init__(self, store_id_or_data, country=COUNTRY_USA, lang='en'):
        self.country = country
        self.urls = Urls(country)
        self.info = {}
        self.menu = None
        
        if isinstance(store_id_or_data, (str, int)):
            # Initialize with store ID - fetch info and menu
            self.id = str(store_id_or_data)
            self._init_from_id(lang)
        elif isinstance(store_id_or_data, dict):
            # Initialize from store data (from nearby stores search)
            self.data = store_id_or_data
            self.id = str(store_id_or_data.get('StoreID', -1))
            self.info = store_id_or_data
        else:
            raise TypeError("store_id_or_data must be a string, int, or dict")
            
    def _init_from_id(self, lang='en'):
        """Initialize store info and menu from store ID."""
        try:
            # Fetch store info
            self.info = request_json(self.urls.info_url(), store_id=self.id)
            
        except Exception as e:
            print(f"Warning: Error fetching store info for {self.id}: {e}")
            self.info = {}
            
        try:
            # Fetch menu
            from .menu import Menu
            self.menu = Menu.from_store(self.id, lang, self.country)
            
        except Exception as e:
            print(f"Warning: Error fetching store menu for {self.id}: {e}")
            self.menu = None

    def get_details(self):
        """Get detailed store information."""
        if not self.info:
            try:
                self.info = request_json(self.urls.info_url(), store_id=self.id)
            except Exception as e:
                print(f"Error fetching store details: {e}")
                return {}
        return self.info

    def get_menu(self, lang='en'):
        """Get the store's menu."""
        if not self.menu:
            try:
                from .menu import Menu
                self.menu = Menu.from_store(self.id, lang, self.country)
            except Exception as e:
                print(f"Error fetching store menu: {e}")
                return None
        return self.menu
        
    @property
    def is_online(self):
        """Check if the store is currently online."""
        return self.info.get('IsOnlineNow', False) or self.data.get('IsOnlineNow', False) if hasattr(self, 'data') else False
        
    @property
    def is_delivery_open(self):
        """Check if delivery service is open."""
        service_info = self.info.get('ServiceIsOpen', {}) or (self.data.get('ServiceIsOpen', {}) if hasattr(self, 'data') else {})
        return service_info.get('Delivery', False)
        
    @property
    def is_carryout_open(self):
        """Check if carryout service is open."""
        service_info = self.info.get('ServiceIsOpen', {}) or (self.data.get('ServiceIsOpen', {}) if hasattr(self, 'data') else {})
        return service_info.get('Carryout', False)
