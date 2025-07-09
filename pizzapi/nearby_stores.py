from .address import Address
from .store import Store
from .utils import request_json
from .urls import Urls, COUNTRY_USA


class NearbyStores:
    """
    Find nearby Dominos stores based on an address.
    
    The NearbyStores class can find stores near a given address and
    filter them based on service type (Delivery, Carryout, etc.).
    """
    
    def __init__(self, address_info=None, pickup_type='Delivery', country=COUNTRY_USA):
        if address_info is None:
            # Default address
            address_info = '222 2nd St, San Francisco, CA 94105'
            
        if isinstance(address_info, str):
            # Parse string address - for now, use a simple split
            parts = address_info.split(', ')
            if len(parts) >= 3:
                street = parts[0]
                city = parts[1]
                state_zip = parts[2].split(' ')
                state = state_zip[0] if state_zip else ''
                zip_code = ' '.join(state_zip[1:]) if len(state_zip) > 1 else ''
                self.address = Address(street, city, state, zip_code, country)
            else:
                # Fallback to default if parsing fails
                self.address = Address('222 2nd St', 'San Francisco', 'CA', '94105', country)
        elif isinstance(address_info, Address):
            self.address = address_info
        else:
            raise TypeError("address_info must be a string or Address object")
            
        self.stores = []
        self.pickup_type = pickup_type
        self.country = country
        self.urls = Urls(country)
        self._dominos_api_response = {}
        
        # Fetch stores
        self._get_stores()
        
    @property
    def dominos_api_response(self):
        """Get the raw Dominos API response."""
        return self._dominos_api_response
        
    @dominos_api_response.setter 
    def dominos_api_response(self, value):
        """Set the raw Dominos API response."""
        if not isinstance(value, dict):
            raise TypeError("dominos_api_response must be a dictionary")
        self._dominos_api_response = value
        
    def _get_stores(self):
        """Fetch nearby stores from the API."""
        try:
            response = request_json(
                self.urls.find_url(),
                line1=self.address.line1,
                line2=self.address.line2, 
                type=self.pickup_type
            )
            
            self.dominos_api_response = response
            
            # Filter and create Store objects
            if 'Stores' in response:
                self.stores = [
                    Store(store_data, self.country) 
                    for store_data in response['Stores']
                    if store_data.get('IsOnlineNow', False) and 
                       store_data.get('ServiceIsOpen', {}).get(self.pickup_type, False)
                ]
            else:
                self.stores = []
                
        except Exception as e:
            print(f"Error fetching nearby stores: {e}")
            self.stores = []
            
    def get_closest_store(self):
        """Get the closest store from the list."""
        if not self.stores:
            return None
        return self.stores[0]  # API usually returns stores sorted by distance
        
    def filter_by_service(self, service_type):
        """Filter stores by service type (Delivery, Carryout, etc.)."""
        filtered_stores = []
        for store in self.stores:
            if hasattr(store, 'data') and store.data.get('ServiceIsOpen', {}).get(service_type, False):
                filtered_stores.append(store)
        return filtered_stores
