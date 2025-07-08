import requests
import xmltodict
import re


def to_pascal_case(data):
    """Convert dictionary keys from snake_case to PascalCase recursively."""
    if isinstance(data, dict):
        return {snake_to_pascal(k): to_pascal_case(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [to_pascal_case(item) for item in data]
    else:
        return data


def to_camel_case(data):
    """Convert dictionary keys from PascalCase to camelCase recursively."""
    if isinstance(data, dict):
        return {pascal_to_camel(k): to_camel_case(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [to_camel_case(item) for item in data]
    else:
        return data


def snake_to_pascal(snake_str):
    """Convert snake_case string to PascalCase."""
    components = snake_str.split('_')
    return ''.join(word.capitalize() for word in components)


def pascal_to_camel(pascal_str):
    """Convert PascalCase string to camelCase."""
    if not pascal_str:
        return pascal_str
    return pascal_str[0].lower() + pascal_str[1:]


def camel_to_snake(camel_str):
    """Convert camelCase/PascalCase string to snake_case."""
    # Insert an underscore before any uppercase letter that follows a lowercase letter
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    # Insert an underscore before any uppercase letter that follows a lowercase letter or number
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def default_parameters(obj, parameters):
    """Merge parameters into object, similar to Object.assign in JavaScript."""
    if not parameters:
        return obj
        
    for key, value in parameters.items():
        # Convert camelCase/PascalCase to snake_case for Python conventions
        snake_key = camel_to_snake(key)
        setattr(obj, snake_key, value)
        
    return obj


# TODO: Find out why this occasionally hangs
# TODO: Can we wrap this up, so the callers don't have to worry about the 
    # complexity of two types of requests? 
def request_json(url, **kwargs):
    """Send a GET request to one of the API endpoints that returns JSON.

    Send a GET request to an endpoint, ideally a URL from the urls module.
    The endpoint is formatted with the kwargs passed to it.

    This will error on an invalid request (requests.Request.raise_for_status()), but will otherwise return a dict.
    """
    r = requests.get(url.format(**kwargs))
    r.raise_for_status()
    return r.json()


def request_xml(url, **kwargs):
    """Send an XML request to one of the API endpoints that returns XML.
    
    This is in every respect identical to request_json. 
    """
    r = requests.get(url.format(**kwargs))
    r.raise_for_status()
    return xmltodict.parse(r.text)
