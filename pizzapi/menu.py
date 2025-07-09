from __future__ import print_function
from .urls import Urls, COUNTRY_USA
from .utils import request_json, to_camel_case, to_pascal_case


class MenuCategory(object):
    """Represents a menu category with subcategories and products."""
    
    def __init__(self, menu_data=None, parent=None):
        self.menu_data = menu_data or {}
        self.subcategories = []
        self.products = []
        self.parent = parent
        self.code = menu_data.get('Code', '') if menu_data else ''
        self.name = menu_data.get('Name', '') if menu_data else ''
        self.description = menu_data.get('Description', '') if menu_data else ''
        self.has_sub_categories = False
        self.has_products = False
        self.has_tags = False

    def get_category_path(self):
        """Get the full path to this category."""
        path = '' if not self.parent else self.parent.get_category_path()
        return path + self.code


class MenuItem(object):
    """Represents a menu item (product, coupon, etc.)."""
    
    def __init__(self, data=None):
        data = data or {}
        self.code = data.get('Code', '')
        self.name = data.get('Name', '')
        self.menu_data = data
        self.categories = []


class Menu(object):
    """    
    The Menu is our primary interface with the API. 

    This is far and away the most complicated class - it wraps up most of
    the logic that parses the information we get from the API.

    The updated Menu class now provides better organized structure
    with proper categorization and easier access to menu items.
    """
    
    def __init__(self, data=None, country=COUNTRY_USA):
        self.country = country
        self.urls = Urls(country)
        self._dominos_api_response = {}
        
        # Initialize menu structure
        self.menu = {
            'categories': {},
            'coupons': {
                'products': {},
                'short_coupon_descriptions': {},
                'coupon_tiers': {},
            },
            'flavors': {},
            'products': {},
            'sides': {},
            'sizes': {},
            'toppings': {},
            'variants': {},
            'preconfigured_products': {},
            'short_product_descriptions': {},
            'unsupported': {
                'products': {},
                'options': {}
            },
            'cooking': {
                'instructions': {},
                'instruction_groups': {}
            }
        }
        
        # Legacy properties for backwards compatibility
        self.variants = {}
        self.menu_by_code = {}
        self.root_categories = {}
        
        if data:
            self._parse_menu_data(data)

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

    @classmethod
    def from_store(cls, store_id, lang='en', country=COUNTRY_USA):
        """Create a Menu instance by fetching data from a specific store."""
        response = request_json(Urls(country).menu_url(), store_id=store_id, lang=lang)
        menu = cls(response, country)
        return menu
        
    def _parse_menu_data(self, data):
        """Parse the menu data from the Dominos API response."""
        self.dominos_api_response = data
        
        # Legacy support - populate old structure
        self.variants = data.get('Variants', {})
        
        if self.variants:
            try:
                self.products = self.parse_items(data.get('Products', {}))
                self.coupons = self.parse_items(data.get('Coupons', {}))
                self.preconfigured = self.parse_items(data.get('PreconfiguredProducts', {}))
                
                # Build category structure
                for key, value in data.get('Categorization', {}).items():
                    try:
                        self.root_categories[key] = self.build_categories(value)
                    except Exception as e:
                        print(f"Warning: Error building category {key}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Warning: Error parsing legacy menu structure: {e}")
                
        # New organized structure
        try:
            self._parse_new_structure(data)
        except Exception as e:
            print(f"Warning: Error parsing new menu structure: {e}")
        
    def _parse_new_structure(self, data):
        """Parse menu data into the new organized structure."""
        try:
            # Define categories
            for category_key, dominos_category in data.get('Categorization', {}).items():
                category = self.menu['categories'][to_camel_case(category_key)] = {}
                self._define_categories(dominos_category.get('Categories', []), category)
        except Exception as e:
            print(f"Warning: Error parsing categories: {e}")
            
        # Parse all sections with error handling
        try:
            self._parse_section(data.get('Flavors', {}), self.menu['flavors'])
            self._parse_section(data.get('Sides', {}), self.menu['sides'])
            self._parse_section(data.get('Sizes', {}), self.menu['sizes'])
            self._parse_section(data.get('Toppings', {}), self.menu['toppings'])
        except Exception as e:
            print(f"Warning: Error parsing menu sections: {e}")
            
        try:
            self._parse_products_section(data.get('Products', {}), self.menu['products'])
            self._parse_products_section(data.get('PreconfiguredProducts', {}), self.menu['preconfigured_products'])
            self._parse_products_section(data.get('Coupons', {}), self.menu['coupons']['products'])
            self._parse_products_section(data.get('Variants', {}), self.menu['variants'])
        except Exception as e:
            print(f"Warning: Error parsing product sections: {e}")
            
        # Additional sections
        try:
            self._parse_simple_section(data.get('ShortProductDescriptions', {}), self.menu['short_product_descriptions'])
            self._parse_simple_section(data.get('UnsupportedProducts', {}), self.menu['unsupported']['products'])
            self._parse_simple_section(data.get('UnsupportedOptions', {}), self.menu['unsupported']['options'])
            self._parse_simple_section(data.get('CookingInstructions', {}), self.menu['cooking']['instructions'])
            self._parse_simple_section(data.get('CookingInstructionGroups', {}), self.menu['cooking']['instruction_groups'])
            self._parse_simple_section(data.get('CouponTiers', {}), self.menu['coupons']['coupon_tiers'])
            self._parse_simple_section(data.get('ShortCouponDescriptions', {}), self.menu['coupons']['short_coupon_descriptions'])
        except Exception as e:
            print(f"Warning: Error parsing additional sections: {e}")
        
    def _define_categories(self, categories, menu_parent):
        """Recursively define category structure."""
        for category in categories:
            formatted_category = menu_parent[to_camel_case(category.get('Code', ''))] = {}
            
            if category.get('Code'):
                formatted_category['code'] = category['Code']
                
            if category.get('Name'):
                formatted_category['name'] = category['Name']
            else:
                formatted_category['name'] = category.get('Code', '')
                
            if category.get('Description'):
                formatted_category['description'] = category['Description']
                
            formatted_category['has_sub_categories'] = False
            
            if category.get('Categories'):
                formatted_category['has_sub_categories'] = True
                formatted_category['sub_categories'] = {}
                self._define_categories(category['Categories'], formatted_category['sub_categories'])
                
            formatted_category['has_products'] = False
            
            if category.get('Products'):
                formatted_category['has_products'] = True
                formatted_category['products'] = category['Products']
                
            formatted_category['has_tags'] = False
            
    def _parse_section(self, dominos_data, menu_section):
        """Parse a section with nested camelCase conversion."""
        if not isinstance(dominos_data, dict):
            return
            
        for key, value in dominos_data.items():
            camel_key = to_camel_case(key)
            menu_section[camel_key] = self._convert_to_camel_case_recursive(value)
            
    def _parse_products_section(self, dominos_data, menu_section):
        """Parse products sections with special handling."""
        if not isinstance(dominos_data, dict):
            return
            
        for key, value in dominos_data.items():
            menu_section[key] = self._convert_to_camel_case_recursive(value)
            
    def _parse_simple_section(self, dominos_data, menu_section):
        """Parse simple sections with camelCase conversion."""
        if not isinstance(dominos_data, dict):
            return
            
        for key, value in dominos_data.items():
            camel_key = to_camel_case(key)
            if isinstance(value, dict):
                menu_section[camel_key] = self._convert_to_camel_case_recursive(value)
            else:
                menu_section[camel_key] = value
                
    def _convert_to_camel_case_recursive(self, data):
        """Recursively convert dictionary keys to camelCase."""
        if isinstance(data, dict):
            return {to_camel_case(k): self._convert_to_camel_case_recursive(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_to_camel_case_recursive(item) for item in data]
        else:
            return data

    # TODO: Reconfigure structure to show that Codes (not ProductCodes) matter
    def build_categories(self, category_data, parent=None):
        category = MenuCategory(category_data, parent)
        for subcategory in category_data['Categories']:
            new_subcategory = self.build_categories(subcategory, category)
            category.subcategories.append(new_subcategory)
        for product_code in category_data['Products']:
            if product_code not in self.menu_by_code:
                # Instead of raising exception, just continue (skip missing products)
                print(f"Warning: Product not found: {product_code} in category {category.code}")
                continue
            product = self.menu_by_code[product_code]
            category.products.append(product)
            product.categories.append(category)
        return category

    def parse_items(self, parent_data):
        items = []
        for code in parent_data.keys():
            obj = MenuItem(parent_data[code])
            self.menu_by_code[obj.code] = obj
            items.append(obj)
        return items

    # TODO: Print codes that can actually be used to order items
    def display(self):
        def print_category(category, depth=1):
            indent = "  " * (depth + 1)
            if len(category.products) + len(category.subcategories) > 0:
                print(indent + category.name)
                for subcategory in category.subcategories:
                    print_category(subcategory, depth + 1)
                for product in category.products:
                    print(indent + "  [%s]" % product.code,
                          product.name.encode('ascii',
                                              'ignore').decode('ascii'))
        print("************ Coupon Menu ************")
        print_category(self.root_categories['Coupons'])
        print("\n************ Preconfigured Menu ************")
        print_category(self.root_categories['PreconfiguredProducts'])
        print("\n************ Regular Menu ************")
        print_category(self.root_categories['Food'])

    # TODO: Find more pythonic way to format the menu
    # TODO: Format the menu after the variants have been filtered
    # TODO: Return the search results and print in different method
    # TODO: Import fuzzy search module or allow lists as search conditions
    def search(self, **conditions):
        """
        Search for menu items based on specified conditions.
        Returns a list of matching items instead of printing them.
        """
        results = []
        if not self.variants:
            print("DEBUG: No variants in menu")
            return results
        
        print(f"DEBUG: Searching {len(self.variants)} variants with conditions: {conditions}")
        
        for v in self.variants.values():
            # Safely handle missing Tags or DefaultToppings
            try:
                if 'Tags' in v and 'DefaultToppings' in v['Tags']:
                    v['Toppings'] = dict(x.split('=', 1) for x in v['Tags']['DefaultToppings'].split(',') if x)
                else:
                    v['Toppings'] = {}
            except (KeyError, AttributeError, ValueError):
                v['Toppings'] = {}
            
            # Check if this variant matches all the search conditions
            matches = True
            for field_name, search_value in conditions.items():
                field_value = v.get(field_name, '')
                
                # Convert both to lowercase strings for case-insensitive comparison
                field_str = str(field_value).lower()
                search_str = str(search_value).lower()
                
                # Check if search term is contained in the field value
                if search_str not in field_str:
                    matches = False
                    break
            
            if matches:
                result = {
                    'Code': v.get('Code', ''),
                    'Name': v.get('Name', '').encode('ascii', 'ignore').decode('ascii'),
                    'Price': v.get('Price', ''),
                    'SizeCode': v.get('SizeCode', ''),
                    'ProductCode': v.get('ProductCode', ''),
                    'Toppings': v.get('Toppings', {}),
                    'FullData': v  # Include full variant data for advanced use
                }
                results.append(result)
        
        print(f"DEBUG: Found {len(results)} matching results")
        return results

    def search_and_print(self, **conditions):
        """
        Legacy method that prints search results (for backwards compatibility).
        """
        results = self.search(**conditions)
        for result in results:
            print(result['Code'], end=' ')
            print(result['Name'], end=' ')
            print('$' + result['Price'], end=' ')
            print(result['SizeCode'], end=' ')
            print(result['ProductCode'], end=' ')
            print(result['Toppings'])
