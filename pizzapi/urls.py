COUNTRY_USA = 'us'
COUNTRY_CANADA = 'ca'

class Urls(object):
    """
    URLs for doing different things to the API.

    This initializes some dicts that contain country-unique information
    on how to interact with the API, and some getter methods for getting
    to that information. These are handy to pass as a first argument to
    pizzapi.utils.request_[xml|json]. 
    """
    def __init__(self, country=COUNTRY_USA):

        self.country = country
        self.urls = {
            COUNTRY_USA: {
                'find_url' : 'https://order.dominos.com/power/store-locator?s={line1}&c={line2}&type={type}',
                'info_url' : 'https://order.dominos.com/power/store/{store_id}/profile',
                'menu_url' : 'https://order.dominos.com/power/store/{store_id}/menu?lang={lang}&structured=true',
                'place_url' : 'https://order.dominos.com/power/place-order',
                'price_url' : 'https://order.dominos.com/power/price-order',
                'track_by_order' : 'https://trkweb.dominos.com/orderstorage/GetTrackerData?StoreID={store_id}&OrderKey={order_key}',
                'track_by_phone' : 'https://trkweb.dominos.com/orderstorage/GetTrackerData?Phone={phone}',
                'validate_url' : 'https://order.dominos.com/power/validate-order',
                'coupon_url' : 'https://order.dominos.com/power/store/{store_id}/coupon/{couponid}?lang={lang}',
                'image_url' : 'https://cache.dominos.com/olo/6_109_0/assets/build/market/US/_en/images/img/products/larges/{product_code}.jpg',
            },
            COUNTRY_CANADA: {
                'find_url' : 'https://order.dominos.ca/power/store-locator?s={line1}&c={line2}&type={type}',
                'info_url' : 'https://order.dominos.ca/power/store/{store_id}/profile',
                'menu_url' : 'https://order.dominos.ca/power/store/{store_id}/menu?lang={lang}&structured=true',
                'place_url' : 'https://order.dominos.ca/power/place-order',
                'price_url' : 'https://order.dominos.ca/power/price-order',
                'track_by_order' : 'https://trkweb.dominos.ca/orderstorage/GetTrackerData?StoreID={store_id}&OrderKey={order_key}',
                'track_by_phone' : 'https://trkweb.dominos.ca/orderstorage/GetTrackerData?Phone={phone}',
                'validate_url' : 'https://order.dominos.ca/power/validate-order',
                'coupon_url' : 'https://order.dominos.ca/power/store/{store_id}/coupon/{couponid}?lang={lang}',
                'image_url' : 'https://cache.dominos.ca/olo/6_109_0/assets/build/market/CA/_en/images/img/products/larges/{product_code}.jpg',
            }
        }
    
    def find_url(self):
        return self.urls[self.country]['find_url']
    
    def info_url(self):
        return self.urls[self.country]['info_url']

    def menu_url(self):
        return self.urls[self.country]['menu_url']

    def place_url(self):
        return self.urls[self.country]['place_url']

    def price_url(self):
        return self.urls[self.country]['price_url']

    def track_by_order(self):
        return self.urls[self.country]['track_by_order']

    def track_by_phone(self):
        return self.urls[self.country]['track_by_phone']
    
    def validate_url(self):
        return self.urls[self.country]['validate_url']
    
    def coupon_url(self):
        return self.urls[self.country]['coupon_url']
    
    def image_url(self):
        return self.urls[self.country]['image_url']



