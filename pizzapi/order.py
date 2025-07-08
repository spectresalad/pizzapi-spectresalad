import requests
from datetime import datetime

from .menu import Menu
from .urls import Urls, COUNTRY_USA
from .dominos_format import DominosFormat
from .amounts_breakdown import AmountsBreakdown
from .address import Address
from .item import Item


class Order(DominosFormat):
    """Core interface to the payments API.

    The Order is perhaps the second most complicated class - it wraps
    up all the logic for actually placing the order, after we've
    determined what we want from the Menu.
    
    Updated with better structure and methods.
    """
    
    def __init__(self, customer=None):
        super().__init__()
        
        # Initialize comprehensive order structure
        self.address = Address('', '', '', '')
        self.amounts = {}
        self.amounts_breakdown = AmountsBreakdown()
        self.business_date = ''
        self.coupons = []
        self.currency = ''
        self.customer_id = ''
        self.estimated_wait_minutes = ''
        self.email = ''
        self.extension = ''
        self.first_name = ''
        self.hotspots_lite = False
        self.ip = ''
        self.last_name = ''
        self.language_code = 'en'
        self.market = ''
        self.meta_data = {'calculateNutrition': True, 'contactless': True}
        self.new_user = True
        self.no_combine = True
        self.order_channel = 'OLO'
        self.order_id = ''
        self.order_info_collection = []
        self.order_method = 'Web'
        self.order_taker = 'python-pizzapi'
        self.partners = {}
        self.payments = []
        self.phone = ''
        self.phone_prefix = ''
        self.price_order_ms = 0
        self.price_order_time = ''
        self.products = []
        self.promotions = {}
        self.pulse_order_guid = ''
        self.service_method = 'Delivery'
        self.source_organization_uri = 'order.dominos.com'
        self.store_id = ''
        self.tags = {}
        self.user_agent = ''
        self.version = '1.0'
        
        # Legacy compatibility properties
        self.store = None
        self.menu = None
        self.customer = None
        
        if customer:
            self.add_customer(customer)
            
    def order_in_future(self, date):
        """Schedule the order for a future date."""
        if not isinstance(date, datetime):
            raise TypeError("Date must be a datetime object")
            
        now = datetime.now()
        if date <= now:
            raise ValueError("Order dates must be in the future")
            
        # Format date for Dominos API
        date_string = date.strftime('%Y-%m-%d %H:%M:%S')
        self.future_order_time = date_string
        
    def order_now(self):
        """Remove future order time to order immediately."""
        if hasattr(self, 'future_order_time'):
            delattr(self, 'future_order_time')
            
    def add_customer(self, customer):
        """Add customer information to the order."""
        if not customer:
            raise ValueError("Customer is required")
            
        self.customer = customer
        
        # Extract customer info
        if hasattr(customer, 'first_name'):
            self.first_name = customer.first_name
        if hasattr(customer, 'last_name'):
            self.last_name = customer.last_name
        if hasattr(customer, 'email'):
            self.email = customer.email
        if hasattr(customer, 'phone'):
            self.phone = customer.phone
        if hasattr(customer, 'address'):
            self.address = customer.address
            
        return self
        
    def add_coupon(self, coupon_code, qty=1):
        """Add a coupon to the order."""
        if isinstance(coupon_code, str):
            # Simple coupon code
            coupon_item = {
                'Code': coupon_code,
                'Qty': qty,
                'ID': len(self.coupons) + 1,
                'isNew': True
            }
        elif isinstance(coupon_code, dict):
            # Coupon object
            coupon_item = coupon_code.copy()
            coupon_item.update({
                'Qty': qty,
                'ID': len(self.coupons) + 1,
                'isNew': True
            })
        else:
            raise TypeError("Coupon must be a string code or dictionary")
            
        self.coupons.append(coupon_item)
        return self
        
    def remove_coupon(self, coupon_code):
        """Remove a coupon from the order."""
        for i, coupon in enumerate(self.coupons):
            if coupon.get('Code') == coupon_code:
                return self.coupons.pop(i)
        raise ValueError(f"Coupon {coupon_code} not found in order")
        
    def add_item(self, item, qty=1):
        """Add an item to the order."""
        if isinstance(item, Item):
            # Item object
            item_data = item.formatted
            item_data['Qty'] = qty
        elif isinstance(item, str):
            # Item code - need menu to get details
            if not self.menu:
                raise ValueError("Menu is required to add items by code")
            if item not in self.menu.variants:
                raise ValueError(f"Item {item} not found in menu")
            item_data = self.menu.variants[item].copy()
            item_data.update({
                'ID': len(self.products) + 1,
                'isNew': True,
                'Qty': qty,
                'AutoRemove': False
            })
        elif isinstance(item, dict):
            # Item dictionary
            item_data = item.copy()
            item_data.update({
                'ID': len(self.products) + 1,
                'isNew': True,
                'Qty': qty,
                'AutoRemove': False
            })
        else:
            raise TypeError("Item must be an Item object, string code, or dictionary")
            
        self.products.append(item_data)
        return item_data
        
    def remove_item(self, item_code):
        """Remove an item from the order."""
        for i, product in enumerate(self.products):
            if product.get('Code') == item_code:
                return self.products.pop(i)
        raise ValueError(f"Item {item_code} not found in order")
        
    def add_payment(self, payment):
        """Add a payment method to the order."""
        if hasattr(payment, 'formatted'):
            payment_data = payment.formatted
        elif isinstance(payment, dict):
            payment_data = payment
        else:
            raise TypeError("Payment must be a Payment object or dictionary")
            
        self.payments.append(payment_data)
        return self

    @property
    def data(self):
        """Get order data in legacy format for backwards compatibility."""
        return {
            'Address': {
                'Street': self.address.street,
                'City': self.address.city,
                'Region': self.address.region,
                'PostalCode': self.address.postal_code,
                'Type': 'House'
            },
            'Coupons': self.coupons,
            'CustomerID': self.customer_id,
            'Extension': self.extension,
            'OrderChannel': self.order_channel,
            'OrderID': self.order_id,
            'NoCombine': self.no_combine,
            'OrderMethod': self.order_method,
            'OrderTaker': self.order_taker,
            'Payments': self.payments,
            'Products': self.products,
            'Market': self.market,
            'Currency': self.currency,
            'ServiceMethod': self.service_method,
            'Tags': self.tags,
            'Version': self.version,
            'SourceOrganizationURI': self.source_organization_uri,
            'LanguageCode': self.language_code,
            'Partners': self.partners,
            'NewUser': self.new_user,
            'metaData': self.meta_data,
            'Amounts': self.amounts,
            'BusinessDate': self.business_date,
            'EstimatedWaitMinutes': self.estimated_wait_minutes,
            'PriceOrderTime': self.price_order_time,
            'AmountsBreakdown': self.amounts_breakdown.formatted if hasattr(self.amounts_breakdown, 'formatted') else {}
        }
    
    def _send(self, url, merge=True, country=COUNTRY_USA):
        """Send order data to the API."""
        urls = Urls(country)
        
        # Prepare data
        order_data = self.formatted
        
        # Add required fields
        order_data.update({
            'StoreID': self.store_id,
            'Email': self.email,
            'FirstName': self.first_name,
            'LastName': self.last_name,
            'Phone': self.phone,
        })
        
        # Validate required fields
        for key in ('Products', 'StoreID', 'Address'):
            if key not in order_data or not order_data[key]:
                raise ValueError(f'Order has invalid value for key "{key}"')
                
        headers = {
            'Referer': 'https://order.dominos.com/en/pages/order/',
            'Content-Type': 'application/json'
        }
        
        try:
            r = requests.post(url=url, headers=headers, json={'Order': order_data})
            r.raise_for_status()
            json_data = r.json()
            
            if merge and 'Order' in json_data:
                # Update order with response data
                for key, value in json_data['Order'].items():
                    if value or not isinstance(value, list):
                        # Convert PascalCase to snake_case for Python
                        snake_key = self._pascal_to_snake(key)
                        if hasattr(self, snake_key):
                            setattr(self, snake_key, value)
                            
            return json_data
            
        except requests.RequestException as e:
            raise Exception(f"Error sending order: {e}")
            
    def _pascal_to_snake(self, pascal_str):
        """Convert PascalCase to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', pascal_str)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        
    def validate(self, country=COUNTRY_USA):
        """Validate the order with the API."""
        urls = Urls(country)
        response = self._send(urls.validate_url(), True, country)
        return response.get('Status', -1) != -1
        
    def price(self, country=COUNTRY_USA):
        """Get pricing for the order."""
        urls = Urls(country)
        response = self._send(urls.price_url(), True, country)
        return response
        
    def place(self, country=COUNTRY_USA):
        """Place the order."""
        urls = Urls(country)
        response = self._send(urls.place_url(), False, country)
        return response
        
    def pay_with(self, payment):
        """Add payment method (legacy compatibility)."""
        return self.add_payment(payment)
