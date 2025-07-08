from .dominos_format import DominosFormat


class Coupon(DominosFormat):
    """Representation of a coupon that can be applied to an order.

    This class represents a coupon that can be added to an Order to get
    discounts on your purchase. It follows the same pattern as the Node.js
    implementation for consistency.
    """
    
    def __init__(self, code, quantity=1):
        """Initialize a coupon.
        
        Args:
            code (str): The coupon code (e.g., 'FREE_PIZZA', '9193')
            quantity (int): The quantity of this coupon to apply (default: 1)
        """
        super().__init__()
        self.code = code
        self.qty = quantity
        self.id = 1
        self.is_new = True
        
    @property
    def formatted(self):
        """Get the coupon data formatted for the Dominos API."""
        return {
            'Code': self.code,
            'Qty': self.qty,
            'ID': self.id,
            'isNew': self.is_new
        }
