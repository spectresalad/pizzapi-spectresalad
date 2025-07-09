from .urls import Urls, COUNTRY_USA
from .utils import request_xml, request_json
from .dominos_format import DominosFormat


class Tracking(DominosFormat):
    """
    Advanced tracking class that provides detailed order tracking information.
    
    This class provides methods to track orders by phone number and gives 
    access to detailed tracking data.
    """
    
    def __init__(self):
        super().__init__()
        self._dominos_phone_api_result = {}
        self._dominos_api_result = {}
        
    @property
    def dominos_phone_api_result(self):
        """Get the raw phone API result."""
        return self._dominos_phone_api_result
        
    @property
    def dominos_api_result(self):
        """Get the raw tracking API result."""
        return self._dominos_api_result
        
    def by_phone(self, phone, country=COUNTRY_USA):
        """Track orders by phone number."""
        if not isinstance(phone, str):
            raise TypeError("Phone number must be a string")
            
        phone = str(phone).strip()
        urls = Urls(country)
        
        try:
            # First get the tracking URL from phone lookup
            track_url = f"{urls.track_by_phone()}?phonenumber={phone}"
            
            # For now, use the legacy XML method to get initial data
            xml_data = request_xml(urls.track_by_phone(), phone=phone)
            self._dominos_phone_api_result = xml_data
            
            # Extract tracking information
            soap_body = xml_data.get('soap:Envelope', {}).get('soap:Body', {})
            response_data = soap_body.get('GetTrackerDataResponse', {})
            order_statuses = response_data.get('OrderStatuses', {})
            
            if 'OrderStatus' in order_statuses:
                order_status = order_statuses['OrderStatus']
                
                # If this is a list, take the first one
                if isinstance(order_status, list):
                    if not order_status:
                        raise Exception('No tracking results found')
                    order_status = order_status[0]
                
                # Try to get more detailed tracking if available
                if 'Actions' in order_status and 'Track' in order_status['Actions']:
                    track_action = order_status['Actions']['Track']
                    detailed_url = f"{urls.track_by_order().split('?')[0]}{track_action}"
                    
                    try:
                        detailed_data = request_json(detailed_url)
                        self._dominos_api_result = detailed_data
                        self.formatted = detailed_data
                    except Exception:
                        # Fall back to basic data
                        self._dominos_api_result = order_status
                        self.formatted = order_status
                else:
                    self._dominos_api_result = order_status
                    self.formatted = order_status
            else:
                raise Exception('No tracking results found')
                
        except Exception as e:
            raise Exception(f'Error tracking order: {e}')
            
        return self
        
    def get_order_status(self):
        """Get a simplified order status."""
        if not self._dominos_api_result:
            return None
            
        return {
            'order_id': self._dominos_api_result.get('OrderID', ''),
            'store_id': self._dominos_api_result.get('StoreID', ''),
            'order_status': self._dominos_api_result.get('OrderStatus', ''),
            'order_description': self._dominos_api_result.get('OrderDescription', ''),
            'start_time': self._dominos_api_result.get('StartTime', ''),
            'estimated_delivery_time': self._dominos_api_result.get('EstimatedDeliveryTime', ''),
        }


def track_by_phone(phone, country=COUNTRY_USA):
    """Query the API to get tracking information.

    Not quite sure what this gets you - problem to solve for next time I get pizza. 
    """
    phone = str(phone).strip()
    data = request_xml(
        Urls(country).track_by_phone(), 
        phone=phone
    )['soap:Envelope']['soap:Body']

    response = data['GetTrackerDataResponse']['OrderStatuses']['OrderStatus']

    return response


def track_by_order(store_id, order_key, country=COUNTRY_USA):
    """Query the API to get tracking information.
    """
    return request_json(
        Urls(country).track_by_order(),
        store_id=store_id,
        order_key=order_key
    )

