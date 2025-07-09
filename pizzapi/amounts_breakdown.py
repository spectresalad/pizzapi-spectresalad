from .dominos_format import DominosFormat


class AmountsBreakdown(DominosFormat):
    """
    Represents a detailed breakdown of order amounts and charges.
    
    The AmountsBreakdown class provides detailed information about
    how the total order amount is calculated, including taxes,
    delivery charges, tips, etc.
    """
    
    def __init__(self, parameters=None):
        super().__init__()
        if parameters:
            self.init = parameters
            
        # Initialize default values
        self.food_and_beverage = 0.0
        self.adjustment = 0.0
        self.surcharge = 0.0
        self.delivery_fee = 0.0
        self.tax = 0.0
        self.tax1 = 0.0
        self.tax2 = 0.0
        self.tax3 = 0.0
        self.tax4 = 0.0
        self.tax5 = 0.0
        self.bottle_deposit = 0.0
        self.customer_total = 0.0
        self.rounding_adjustment = 0.0
        self.cash = 0.0
        self.savings = 0.0
        
    def calculate_total(self):
        """Calculate the total amount from all components."""
        total = (
            self.food_and_beverage +
            self.adjustment +
            self.surcharge +
            self.delivery_fee +
            self.tax +
            self.tax1 +
            self.tax2 +
            self.tax3 +
            self.tax4 +
            self.tax5 +
            self.bottle_deposit +
            self.rounding_adjustment
        )
        return round(total, 2)
        
    def get_total_tax(self):
        """Get the total tax amount from all tax fields."""
        total_tax = (
            self.tax +
            self.tax1 +
            self.tax2 +
            self.tax3 +
            self.tax4 +
            self.tax5
        )
        return round(total_tax, 2)
        
    def __str__(self):
        """Return a string representation of the amounts breakdown."""
        lines = [
            f"Food & Beverage: ${self.food_and_beverage:.2f}",
            f"Delivery Fee: ${self.delivery_fee:.2f}",
            f"Tax: ${self.get_total_tax():.2f}",
            f"Adjustments: ${self.adjustment:.2f}",
            f"Surcharge: ${self.surcharge:.2f}",
            f"Bottle Deposit: ${self.bottle_deposit:.2f}",
            f"Rounding: ${self.rounding_adjustment:.2f}",
            f"Savings: ${self.savings:.2f}",
            f"Total: ${self.calculate_total():.2f}"
        ]
        return '\n'.join(lines)
