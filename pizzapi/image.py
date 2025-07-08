import base64
import requests
from .urls import Urls, COUNTRY_USA


class Image:
    """Handles fetching and processing product images from Dominos API.
    
    The Image class can fetch product images and convert them to base64
    for use in applications.
    """
    
    def __init__(self, product_code, country=COUNTRY_USA):
        if not isinstance(product_code, str):
            raise TypeError("product_code must be a string")
            
        self.product_code = product_code
        self.urls = Urls(country)
        self.base64_image = None
        
        # Fetch the image
        self._fetch_image()
        
    def _fetch_image(self):
        """Fetch the product image and convert to base64."""
        try:
            url = self.urls.image_url().format(product_code=self.product_code)
            response = requests.get(url)
            response.raise_for_status()
            
            # Convert to base64
            self.base64_image = base64.b64encode(response.content).decode('utf-8')
            
        except requests.RequestException as e:
            print(f"Error fetching image for product {self.product_code}: {e}")
            self.base64_image = None
            
    def save_to_file(self, filename):
        """Save the image to a file."""
        if not self.base64_image:
            raise ValueError("No image data available")
            
        try:
            image_data = base64.b64decode(self.base64_image)
            with open(filename, 'wb') as f:
                f.write(image_data)
        except Exception as e:
            raise RuntimeError(f"Error saving image to {filename}: {e}")
            
    def get_data_url(self, mime_type='image/jpeg'):
        """Get a data URL for the image suitable for use in HTML/CSS."""
        if not self.base64_image:
            return None
        return f"data:{mime_type};base64,{self.base64_image}"
