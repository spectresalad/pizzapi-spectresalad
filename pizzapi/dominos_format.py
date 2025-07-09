import json
from .utils import to_pascal_case, to_camel_case, default_parameters


class DominosFormat:
    """
    Base class that provides common formatting functionality for Dominos API objects.
    
    This class handles the conversion between Python snake_case conventions
    and the Dominos API's PascalCase/camelCase requirements.
    """
    
    def __init__(self):
        self._dominos_api_response = {}
        
    @property
    def init(self):
        """Get initialization parameters."""
        return None
        
    @init.setter
    def init(self, parameters):
        """Set initialization parameters and merge them into this object."""
        if parameters:
            default_parameters(self, parameters)
            
    @property
    def formatted(self):
        """Get the object formatted for the Dominos API (PascalCase keys)."""
        # Create a deep copy of the object's data
        data = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                data[key] = value
                
        # Convert to PascalCase for Dominos API
        return to_pascal_case(data)
        
    @formatted.setter
    def formatted(self, dominos_data):
        """Set object properties from Dominos API response data."""
        if dominos_data:
            # Convert from PascalCase/camelCase to snake_case
            camel_data = to_camel_case(dominos_data)
            for key, value in camel_data.items():
                setattr(self, key, value)
                
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
