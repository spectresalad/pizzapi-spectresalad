from .dominos_format import DominosFormat


class Item(DominosFormat):
    """Represents a menu item that can be added to an order.
    
    The Item class extends DominosFormat to provide proper formatting
    for the Dominos API. Items can be products, sides, drinks, etc.
    """
    
    _id_counter = 1
    
    def __init__(self, parameters=None):
        super().__init__()
        if parameters:
            self.init = parameters
        
        self.id = Item._id_counter
        Item._id_counter += 1
        
        self.code = ''
        self.qty = 1
        self.options = {}
        self.is_new = True
        
    @property
    def formatted(self):
        """Get the formatted representation for the Dominos API."""
        formatted = super().formatted
        formatted['IsNew'] = self.is_new
        return formatted
        
    @formatted.setter
    def formatted(self, value):
        """Set values from formatted Dominos API response."""
        super(Item, self.__class__).formatted.fset(self, value)
