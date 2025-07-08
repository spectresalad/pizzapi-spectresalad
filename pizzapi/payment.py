import re
from .dominos_format import DominosFormat


class PaymentObject(DominosFormat):
    """A PaymentObject represents a credit card.

    There's some sweet logic in here to make sure that the type of card
    you passed is valid. 
    
    Updated with better validation and formatting.
    """
    
    def __init__(self, parameters=None):
        super().__init__()
        
        # Initialize default values
        self.type = 'CreditCard'
        self.amount = 0.0
        self.tip_amount = 0.0
        self.number = ''
        self.card_type = ''
        self.expiration = ''
        self.security_code = ''
        self.postal_code = ''
        self.name = ''
        
        if parameters:
            # Validate required fields
            if not parameters.get('number'):
                raise ValueError("Credit card number is required")
            if not parameters.get('expiration'):
                raise ValueError("Expiration date is required")
            if not parameters.get('security_code'):
                raise ValueError("Security code is required")
            if not parameters.get('postal_code'):
                raise ValueError("Postal code is required")
                
            # Process and validate card number
            self.number = self._digits_only(str(parameters['number']))
            self.card_type = self._validate_and_find_type(self.number)
            
            if not self.card_type:
                raise ValueError("Invalid credit card number")
                
            # Set other fields
            self.expiration = self._digits_only(str(parameters['expiration']))
            self.security_code = str(parameters['security_code']).strip()
            self.postal_code = str(parameters['postal_code']).strip()
            self.amount = float(parameters.get('amount', 0))
            self.tip_amount = float(parameters.get('tip_amount', 0))
            
            if 'name' in parameters:
                self.name = str(parameters['name']).strip()
                
    def _digits_only(self, string):
        """Extract only digits from a string."""
        return re.sub(r'\D', '', string)
        
    def _validate_and_find_type(self, number):
        """Validate card number and determine card type."""
        if not number or not number.isdigit():
            return ''
            
        patterns = {
            'VISA': r'^4[0-9]{12}(?:[0-9]{3})?$',
            'MASTERCARD': r'^5[1-5][0-9]{14}$',
            'AMEX': r'^3[47][0-9]{13}$',
            'DINERS': r'^3(?:0[0-5]|[68][0-9])[0-9]{11}$',
            'DISCOVER': r'^6(?:011|5[0-9]{2})[0-9]{12}$',
            'JCB': r'^(?:2131|1800|35\d{3})\d{11}$',
            'ENROUTE': r'^(?:2014|2149)\d{11}$'
        }
        
        for card_type, pattern in patterns.items():
            if re.match(pattern, number):
                return card_type
                
        return ''

    def validate(self):
        """Validate the payment object."""
        is_valid = bool(self.number and self.card_type and self.expiration)
        is_valid &= bool(re.match(r'^[0-9]{3,4}$', self.security_code))
        is_valid &= bool(re.match(r'^[0-9]{5}(?:-[0-9]{4})?$', self.postal_code))
        return is_valid

    def find_type(self):
        """Legacy method for backwards compatibility."""
        return self.card_type


# Legacy alias
Payment = PaymentObject
