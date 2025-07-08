from .store import Store
from .utils import request_json
from .urls import Urls, COUNTRY_USA
from .dominos_format import DominosFormat
import re


class Address(DominosFormat):
    """Create an address, for finding stores and placing orders.

    The Address object describes a street address in North America (USA or
    Canada, for now). Callers can use the Address object's methods to find
    the closest or nearby stores from the API. 

    Attributes:
        street (String): Street address
        street_number (String): Street number  
        street_name (String): Street name
        unit_type (String): Unit type (Apt, Suite, etc.)
        unit_number (String): Unit number
        city (String): North American city
        region (String): North American region (state, province, territory)
        postal_code (String): North American ZIP/postal code
        delivery_instructions (String): Special delivery instructions
        urls (String): Country-specific URLs
        country (String): Country
    """

    def __init__(self, street='', city='', region='', zip='', country=COUNTRY_USA, *args):
        super().__init__()
        
        # Handle string parsing
        if isinstance(street, str) and not city and not region and not zip:
            self._parse_address_string(street)
        else:
            self.street = str(street).strip()
            self.city = str(city).strip()
            self.region = str(region).strip()
            self.postal_code = str(zip).strip()
            
        # Additional address fields
        self.street_number = ''
        self.street_name = ''
        self.unit_type = ''
        self.unit_number = ''
        self.delivery_instructions = ''
        
        self.urls = Urls(country)
        self.country = country
        
    def _parse_address_string(self, address_string):
        """Parse a full address string into components."""
        # Simple parsing - can be enhanced
        parts = address_string.split(', ')
        
        if len(parts) >= 3:
            self.street = parts[0].strip()
            self.city = parts[1].strip()
            
            # Handle state and zip
            state_zip = parts[2].strip()
            state_zip_parts = state_zip.split(' ')
            if len(state_zip_parts) >= 2:
                self.region = state_zip_parts[0]
                self.postal_code = ' '.join(state_zip_parts[1:])
            else:
                self.region = state_zip
                self.postal_code = ''
        elif len(parts) == 2:
            self.street = parts[0].strip()
            city_state = parts[1].strip()
            # Try to split city and state
            city_state_parts = city_state.rsplit(' ', 1)
            if len(city_state_parts) == 2:
                self.city = city_state_parts[0]
                self.region = city_state_parts[1]
            else:
                self.city = city_state
                self.region = ''
            self.postal_code = ''
        else:
            self.street = address_string.strip()
            self.city = ''
            self.region = ''
            self.postal_code = ''

    @property
    def data(self):
        return {'Street': self.street, 'City': self.city,
                'Region': self.region, 'PostalCode': self.postal_code}

    @property
    def line1(self):
        """Get the first line of the address."""
        if self.street:
            return self.street
        elif self.street_number and self.street_name:
            unit_part = f" {self.unit_type} {self.unit_number}".strip() if self.unit_type or self.unit_number else ""
            return f"{self.street_number} {self.street_name}{unit_part}".strip()
        else:
            return ''

    @property
    def line2(self):
        """Get the second line of the address."""
        return f"{self.city} {self.region} {self.postal_code}".strip()
        
    @property
    def address_lines(self):
        """Get address lines as a dictionary."""
        return {
            'line1': self.line1,
            'line2': self.line2
        }

    def nearby_stores(self, service='Delivery'):
        """Query the API to find nearby stores.

        nearby_stores will filter the information we receive from the API
        to exclude stores that are not currently online (!['IsOnlineNow']),
        and stores that are not currently in service (!['ServiceIsOpen']).
        """
        data = request_json(self.urls.find_url(), line1=self.line1, line2=self.line2, type=service)
        return [Store(x, self.country) for x in data['Stores']
                if x['IsOnlineNow'] and x['ServiceIsOpen'][service]]

    def closest_store(self, service='Delivery'):
        stores = self.nearby_stores(service=service)
        if not stores:
            raise Exception('No local stores are currently open')
        return stores[0]
