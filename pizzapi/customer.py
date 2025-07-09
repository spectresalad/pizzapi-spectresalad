from .address import Address
from .dominos_format import DominosFormat


class Customer(DominosFormat):
    """
    The Customer orders a pizza.

    You need a Customer to create an Order. The proprietors of the API
    use this information, presumably for nefarious Pizza Purposes.
    
    The Customer class now extends DominosFormat to provide proper
    formatting for the Dominos API.
    """

    def __init__(self, parameters=None):
        super().__init__()
        
        # Initialize default values
        self.first_name = ''
        self.last_name = ''
        self.email = ''
        self.phone = ''
        self.phone_prefix = ''
        self.address = Address('', '', '', '')
        
        if parameters:
            self.init = parameters
            
            # Handle address specially if provided
            if 'address' in parameters and parameters['address']:
                if isinstance(parameters['address'], Address):
                    self.address = parameters['address']
                elif isinstance(parameters['address'], dict):
                    self.address = Address(
                        street=parameters['address'].get('street', ''),
                        city=parameters['address'].get('city', ''),
                        region=parameters['address'].get('region', ''),
                        zip=parameters['address'].get('zip', ''),
                        country=parameters['address'].get('country', 'us')
                    )
                    
            # Clean up phone number
            if hasattr(self, 'phone') and self.phone:
                self.phone = str(self.phone).replace('-', '').replace('(', '').replace(')', '').replace(' ', '')

