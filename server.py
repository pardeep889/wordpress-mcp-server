# mcp_wp_server.py

import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
import requests
import base64

load_dotenv()

mcp = FastMCP("wordpress_mcp")

DEFAULT_SITE_URL = os.environ.get('WORDPRESS_SITE_URL', '')
DEFAULT_JWT_TOKEN = os.environ.get('WORDPRESS_JWT_TOKEN', '')
DEFAULT_WOCOMMERCE_CONSUMER_KEY = os.environ.get('WOCOMMERCE_CONSUMER_KEY', '')
DEFAULT_WOCOMMERCE_CONSUMER_SECRET = os.environ.get('WOCOMMERCE_CONSUMER_SECRET', '')

def get_wp_client(site_url=None, jwt_token=None, wpe_auth_cookie=None):
    site_url = site_url or DEFAULT_SITE_URL
    jwt_token = jwt_token or DEFAULT_JWT_TOKEN
    if not site_url or not jwt_token:
        raise Exception('Site URL or JWT token not provided')

    base_url = f"{site_url}/wp-json/wp/v2"
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'User-Agent': 'curl/7.64.1',
    }
    return base_url, headers

@mcp.tool()
def create_post(title: str, content: str, status: str = "draft", site_url: str = "", jwt_token: str = "") -> dict:
   base_url, headers = get_wp_client(site_url, jwt_token)
   data = {'title': title, 'content': content, 'status': status}
   response = requests.post(f"{base_url}/posts", json=data, headers=headers)
   response.raise_for_status()
   return response.json()

@mcp.tool()
def get_posts(per_page: int = 10, page: int = 1, site_url: str = "", jwt_token: str = "") -> list:
   base_url, headers = get_wp_client(site_url, jwt_token)
   query = {'per_page': per_page, 'page': page}
   response = requests.get(f"{base_url}/posts", params=query, headers=headers)
   response.raise_for_status()
   return response.json()

@mcp.tool()
def update_post(post_id: int, title: str = "", content: str = "", status: str = "", site_url: str = "", jwt_token: str = "") -> dict:
   base_url, headers = get_wp_client(site_url, jwt_token)
   data = {}
   if title: data['title'] = title
   if content: data['content'] = content
   if status: data['status'] = status
   response = requests.post(f"{base_url}/posts/{post_id}", json=data, headers=headers)
   response.raise_for_status()
   return response.json()



@mcp.tool()
def delete_post(post_id: int, site_url: str = "", jwt_token: str = "") -> dict:
    """
    Delete a WordPress post by its ID.

    Args:
        post_id (int): The ID of the post to delete.
        site_url (str): The base URL of the WordPress site.
        jwt_token (str): The JWT authentication token.

    Returns:
        dict: The response from the WordPress API.
    """
    base_url, headers = get_wp_client(site_url, jwt_token)
    url = f"{base_url}/posts/{post_id}"
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response.json()







# ----------------------------WOO COMMERCE --------------------------------------------------------------------

def get_woo_client(site_url=None, consumer_key=None, consumer_secret=None):
    site_url = site_url or DEFAULT_SITE_URL
    consumer_key = consumer_key or DEFAULT_WOCOMMERCE_CONSUMER_KEY
    consumer_secret = consumer_secret or DEFAULT_WOCOMMERCE_CONSUMER_SECRET

    if not consumer_key or not consumer_secret:
        raise Exception('WooCommerce credentials not provided')
        
    base_url = f"{site_url}/wp-json/wc/v3"
    # Prepare HTTP Basic Auth header
    user_pass = f"{consumer_key}:{consumer_secret}"
    b64_auth = base64.b64encode(user_pass.encode()).decode()
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'curl/7.64.1',
        'Authorization': f'Basic {b64_auth}'
    }
    return base_url, headers

@mcp.tool()
def get_orders(per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'per_page': per_page, 'page': page}
    try:
        print('MCP get_orders request:')
        print('URL:', f"{base_url}/orders")
        print('Headers:', headers)
        print('Params:', params)
        response = requests.get(f"{base_url}/orders", params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print('MCP get_orders error:', str(e))
        if hasattr(e, 'response') and e.response is not None:
            print('Response text:', e.response.text)
        raise

@mcp.tool()
def create_order(order_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Create a new WooCommerce order.

    Args:
        order_data (dict): Dictionary containing order information. Required fields:
            - payment_details (dict): Payment information
                - method_id (str): Payment method ID
                - method_title (str): Payment method title
                - paid (bool): Whether the order is paid
            - billing_address (dict): Billing address information
                - first_name (str): First name
                - last_name (str): Last name
                - address_1 (str): Address line 1
                - address_2 (str, optional): Address line 2
                - city (str): City
                - state (str): State/Province
                - postcode (str): Postal code
                - country (str): Country code
                - email (str): Email address
                - phone (str): Phone number
            - shipping_address (dict): Shipping address information
                - first_name (str): First name
                - last_name (str): Last name
                - address_1 (str): Address line 1
                - address_2 (str, optional): Address line 2
                - city (str): City
                - state (str): State/Province
                - postcode (str): Postal code
                - country (str): Country code
            - customer_id (int): Customer ID
            - line_items (list): List of order items
                Each item is a dict with:
                - product_id (int): Product ID
                - quantity (int): Quantity
                - variations (dict, optional): Product variations
            - shipping_lines (list): Shipping methods
                Each item is a dict with:
                - method_id (str): Shipping method ID
                - method_title (str): Shipping method title
                - total (str): Shipping cost as string
            Optional fields:
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The created order data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.post(f"{base_url}/orders", json=order_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_order(order_id: int, order_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Update an existing WooCommerce order.

    Args:
        order_id (int): The ID of the order to update.
        order_data (dict): Dictionary containing order information to update. Updatable fields:
            - payment_details (dict): Payment information
                - method_id (str): Payment method ID
                - method_title (str): Payment method title
                - paid (bool): Whether the order is paid
            - billing_address (dict): Billing address information
                - first_name (str): First name
                - last_name (str): Last name
                - address_1 (str): Address line 1
                - address_2 (str, optional): Address line 2
                - city (str): City
                - state (str): State/Province
                - postcode (str): Postal code
                - country (str): Country code
                - email (str): Email address
                - phone (str): Phone number
            - shipping_address (dict): Shipping address information
                - first_name (str): First name
                - last_name (str): Last name
                - address_1 (str): Address line 1
                - address_2 (str, optional): Address line 2
                - city (str): City
                - state (str): State/Province
                - postcode (str): Postal code
                - country (str): Country code
            - customer_id (int): Customer ID
            - line_items (list): List of order items
                Each item is a dict with:
                - product_id (int): Product ID
                - quantity (int): Quantity
                - variations (dict, optional): Product variations
            - shipping_lines (list): Shipping methods
                Each item is a dict with:
                - method_id (str): Shipping method ID
                - method_title (str): Shipping method title
                - total (str): Shipping cost as string
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The updated order data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.put(f"{base_url}/orders/{order_id}", json=order_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_order(order_id: int, force: bool = True, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Delete a WooCommerce order.

    Args:
        order_id (int): The ID of the order to delete.
        force (bool): Whether to permanently delete the order (True) or move to trash (False).
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The response from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'force': force}
    response = requests.delete(f"{base_url}/orders/{order_id}", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_products(per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'per_page': per_page, 'page': page}
    response = requests.get(f"{base_url}/products", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_product(product_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Create a new WooCommerce product.

    Args:
        product_data (dict): Dictionary containing product information. Required fields:
            - name (str): Product name
            - type (str): Product type ('simple', 'variable', 'grouped', or 'external')
            - regular_price (str): Regular price of the product
            - description (str): Product description
            Optional fields:
            - short_description (str): Product short description
            - categories (list): List of category IDs
            - images (list): List of image objects
            - attributes (list): List of attribute objects
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The created product data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)  # Moved this line up

    print('MCP create_product request:')
    print('URL:', f"{base_url}/products")
    print('Headers:', headers)
    print('Params:', product_data)

    response = requests.post(f"{base_url}/products", json=product_data, headers=headers)
    response.raise_for_status()
    return response.json()
@mcp.tool()
def update_product(product_id: int, product_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Update an existing WooCommerce product.

    Args:
        product_id (int): The ID of the product to update.
        product_data (dict): Dictionary containing product information to update. Possible fields:
            - name (str): Product name
            - type (str): Product type ('simple', 'variable', 'grouped', or 'external')
            - regular_price (str): Regular price of the product
            - description (str): Product description
            - short_description (str): Product short description
            - categories (list): List of category IDs
            - images (list): List of image objects
            - attributes (list): List of attribute objects
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The updated product data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.put(f"{base_url}/products/{product_id}", json=product_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_product(product_id: int, force: bool = True, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Delete a WooCommerce product.

    Args:
        product_id (int): The ID of the product to delete.
        force (bool): Whether to permanently delete the product (True) or move to trash (False).
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The response from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'force': force}
    response = requests.delete(f"{base_url}/products/{product_id}", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_product_categories(per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'per_page': per_page, 'page': page}
    response = requests.get(f"{base_url}/products/categories", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_product_category(category_id: int, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/products/categories/{category_id}", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_product_category(category_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Create a new WooCommerce product category.

    Args:
        category_data (dict): Dictionary containing category information. Required fields:
            - name (str): Category name
            - slug (str): Category slug (URL-friendly version of the name)
            Optional fields:
            - description (str): Category description
            - parent (int): ID of the parent category (0 for top-level category)
            - display (str): Category display type ('default', 'products', 'subcategories', or 'both')
            - image (dict): Category image data
            - menu_order (int): Menu order for the category
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The created category data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.post(f"{base_url}/products/categories", json=category_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_product_category(category_id: int, category_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Update an existing WooCommerce product category.

    Args:
        category_id (int): The ID of the category to update.
        category_data (dict): Dictionary containing category information to update. Possible fields:
            - name (str): Category name
            - slug (str): Category slug (URL-friendly version of the name)
            - description (str): Category description
            - parent (int): ID of the parent category
            - display (str): Category display type ('default', 'products', 'subcategories', or 'both')
            - image (dict): Category image data
            - menu_order (int): Menu order for the category
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The updated category data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.put(f"{base_url}/products/categories/{category_id}", json=category_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_product_category(category_id: int, force: bool = True, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Delete a WooCommerce product category.

    Args:
        category_id (int): The ID of the category to delete.
        force (bool): Whether to permanently delete the category (True) or move to trash (False).
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The response from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'force': force}
    response = requests.delete(f"{base_url}/products/categories/{category_id}", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_customers(per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'per_page': per_page, 'page': page}
    response = requests.get(f"{base_url}/customers", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_customer(customer_id: int, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/customers/{customer_id}", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_customer(customer_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Create a new WooCommerce customer.

    Args:
        customer_data (dict): Dictionary containing customer information. Required fields:
            - email (str): Customer email address
            - first_name (str): Customer first name
            - last_name (str): Customer last name
            Optional fields:
            - username (str): Customer username
            - billing (dict): Billing address information
            - shipping (dict): Shipping address information
            - is_paying_customer (bool): Whether the customer has made a purchase
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The created customer data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.post(f"{base_url}/customers", json=customer_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_customer(customer_id: int, customer_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Update an existing WooCommerce customer.

    Args:
        customer_id (int): The ID of the customer to update.
        customer_data (dict): Dictionary containing customer information to update. Possible fields:
            - email (str): Customer email address
            - first_name (str): Customer first name
            - last_name (str): Customer last name
            - username (str): Customer username
            - billing (dict): Billing address information
            - shipping (dict): Shipping address information
            - is_paying_customer (bool): Whether the customer has made a purchase
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The updated customer data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.put(f"{base_url}/customers/{customer_id}", json=customer_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_customer(customer_id: int, force: bool = True, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Delete a WooCommerce customer.

    Args:
        customer_id (int): The ID of the customer to delete.
        force (bool): Whether to permanently delete the customer (True) or move to trash (False).
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The response from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'force': force}
    response = requests.delete(f"{base_url}/customers/{customer_id}", params=params, headers=headers)
    response.raise_for_status()
    return response.json()


# --- Product Variations ---
@mcp.tool()
def get_product_variations(product_id: int, per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'per_page': per_page, 'page': page}
    response = requests.get(f"{base_url}/products/{product_id}/variations", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_product_variation(product_id: int, variation_id: int, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/products/{product_id}/variations/{variation_id}", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_product_variation(product_id: int, variation_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Create a new WooCommerce product variation.

    Args:
        product_id (int): The ID of the parent product.
        variation_data (dict): Dictionary containing variation information. Required fields:
            - regular_price (str): Regular price of the variation
            - attributes (list): List of variation attributes
            Optional fields:
            - sale_price (str): Sale price of the variation
            - sku (str): Stock Keeping Unit
            - stock_quantity (int): Stock quantity
            - image (dict): Variation image data
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The created variation data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.post(f"{base_url}/products/{product_id}/variations", json=variation_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_product_variation(product_id: int, variation_id: int, variation_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Update an existing WooCommerce product variation.

    Args:
        product_id (int): The ID of the parent product.
        variation_id (int): The ID of the variation to update.
        variation_data (dict): Dictionary containing variation information to update. Possible fields:
            - regular_price (str): Regular price of the variation
            - sale_price (str): Sale price of the variation
            - sku (str): Stock Keeping Unit
            - stock_quantity (int): Stock quantity
            - attributes (list): List of variation attributes
            - image (dict): Variation image data
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The updated variation data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.put(f"{base_url}/products/{product_id}/variations/{variation_id}", json=variation_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_product_variation(product_id: int, variation_id: int, force: bool = True, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Delete a WooCommerce product variation.

    Args:
        product_id (int): The ID of the parent product.
        variation_id (int): The ID of the variation to delete.
        force (bool): Whether to permanently delete the variation (True) or move to trash (False).
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The response from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'force': force}
    response = requests.delete(f"{base_url}/products/{product_id}/variations/{variation_id}", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

# --- Product Attributes ---
@mcp.tool()
def get_product_attributes(per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'per_page': per_page, 'page': page}
    response = requests.get(f"{base_url}/products/attributes", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_product_attribute(attribute_id: int, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/products/attributes/{attribute_id}", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_product_attribute(attribute_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Create a new WooCommerce product attribute.

    Args:
        attribute_data (dict): Dictionary containing attribute information. Required fields:
            - name (str): Attribute name
            - type (str): Attribute type ('select', 'radio', 'checkbox', 'text', or 'textarea')
            Optional fields:
            - slug (str): Attribute slug (URL-friendly version of the name)
            - order_by (str): Order by ('menu_order', 'name', or 'id')
            - has_archives (bool): Whether to enable archives for this attribute
            - options (list): List of attribute terms
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The created attribute data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.post(f"{base_url}/products/attributes", json=attribute_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_product_attribute(attribute_id: int, attribute_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Update an existing WooCommerce product attribute.

    Args:
        attribute_id (int): The ID of the attribute to update.
        attribute_data (dict): Dictionary containing attribute information to update. Possible fields:
            - name (str): Attribute name
            - type (str): Attribute type ('select', 'radio', 'checkbox', 'text', or 'textarea')
            - slug (str): Attribute slug (URL-friendly version of the name)
            - order_by (str): Order by ('menu_order', 'name', or 'id')
            - has_archives (bool): Whether to enable archives for this attribute
            - options (list): List of attribute terms
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The updated attribute data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.put(f"{base_url}/products/attributes/{attribute_id}", json=attribute_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_product_attribute(attribute_id: int, force: bool = True, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Delete a WooCommerce product attribute.

    Args:
        attribute_id (int): The ID of the attribute to delete.
        force (bool): Whether to permanently delete the attribute (True) or move to trash (False).
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The response from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'force': force}
    response = requests.delete(f"{base_url}/products/attributes/{attribute_id}", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

# --- Product Attribute Terms ---
@mcp.tool()
def get_attribute_terms(attribute_id: int, per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'per_page': per_page, 'page': page}
    response = requests.get(f"{base_url}/products/attributes/{attribute_id}/terms", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_attribute_term(attribute_id: int, term_id: int, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/products/attributes/{attribute_id}/terms/{term_id}", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_attribute_term(attribute_id: int, term_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Create a new WooCommerce attribute term.

    Args:
        attribute_id (int): The ID of the attribute to create a term for.
        term_data (dict): Dictionary containing term information. Required fields:
            - name (str): Term name
            - slug (str): Term slug (URL-friendly version of the name)
            Optional fields:
            - description (str): Term description
            - menu_order (int): Menu order for the term
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The created term data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.post(f"{base_url}/products/attributes/{attribute_id}/terms", json=term_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_attribute_term(attribute_id: int, term_id: int, term_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Update an existing WooCommerce attribute term.

    Args:
        attribute_id (int): The ID of the attribute containing the term.
        term_id (int): The ID of the term to update.
        term_data (dict): Dictionary containing term information to update. Possible fields:
            - name (str): Term name
            - slug (str): Term slug (URL-friendly version of the name)
            - description (str): Term description
            - menu_order (int): Menu order for the term
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The updated term data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.put(f"{base_url}/products/attributes/{attribute_id}/terms/{term_id}", json=term_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_attribute_term(attribute_id: int, term_id: int, force: bool = True, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Delete a WooCommerce attribute term.

    Args:
        attribute_id (int): The ID of the attribute containing the term.
        term_id (int): The ID of the term to delete.
        force (bool): Whether to permanently delete the term (True) or move to trash (False).
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The response from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'force': force}
    response = requests.delete(f"{base_url}/products/attributes/{attribute_id}/terms/{term_id}", params=params, headers=headers)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_product_tags(per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'per_page': per_page, 'page': page}
    response = requests.get(f"{base_url}/products/tags", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_product_tag(tag_id: int, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/products/tags/{tag_id}", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_product_tag(tag_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Create a new WooCommerce product tag.

    Args:
        tag_data (dict): Dictionary containing tag information. Required fields:
            - name (str): Tag name
            - slug (str): Tag slug (URL-friendly version of the name)
            Optional fields:
            - description (str): Tag description
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The created tag data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.post(f"{base_url}/products/tags", json=tag_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_product_tag(tag_id: int, tag_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Update an existing WooCommerce product tag.

    Args:
        tag_id (int): The ID of the tag to update.
        tag_data (dict): Dictionary containing tag information to update. Possible fields:
            - name (str): Tag name
            - slug (str): Tag slug (URL-friendly version of the name)
            - description (str): Tag description
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The updated tag data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.put(f"{base_url}/products/tags/{tag_id}", json=tag_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_product_tag(tag_id: int, force: bool = True, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Delete a WooCommerce product tag.

    Args:
        tag_id (int): The ID of the tag to delete.
        force (bool): Whether to permanently delete the tag (True) or move to trash (False).
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The response from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'force': force}
    response = requests.delete(f"{base_url}/products/tags/{tag_id}", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_product_reviews(product_id: int = None, per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    url = f"{base_url}/products/reviews"
    params = {'per_page': per_page, 'page': page}
    if product_id:
        params['product'] = product_id
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_product_review(review_id: int, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    url = f"{base_url}/products/reviews/{review_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_product_review(product_id: int, review_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Create a new WooCommerce product review.

    Args:
        product_id (int): The ID of the product being reviewed.
        review_data (dict): Dictionary containing review information. Required fields:
            - review (str): The review content
            - rating (int): The rating (1-5)
            - reviewer (str): The reviewer's name
            - reviewer_email (str): The reviewer's email
            Optional fields:
            - status (str): Review status ('approved', 'pending', 'spam', 'trash')
            - reviewer_avatar_urls (dict): Dictionary of avatar URLs
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The created review data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    # Ensure product_id is in the review_data
    review_data = dict(review_data)
    review_data['product_id'] = product_id
    response = requests.post(f"{base_url}/products/reviews", json=review_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_product_review(review_id: int, review_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Update an existing WooCommerce product review.

    Args:
        review_id (int): The ID of the review to update.
        review_data (dict): Dictionary containing review information to update. Possible fields:
            - review (str): The review content
            - rating (int): The rating (1-5)
            - reviewer (str): The reviewer's name
            - reviewer_email (str): The reviewer's email
            - status (str): Review status ('approved', 'pending', 'spam', 'trash')
            - reviewer_avatar_urls (dict): Dictionary of avatar URLs
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The updated review data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    url = f"{base_url}/products/reviews/{review_id}"
    response = requests.put(url, json=review_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_product_review(review_id: int, force: bool = True, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Delete a WooCommerce product review.

    Args:
        review_id (int): The ID of the review to delete.
        force (bool): Whether to permanently delete the review (True) or move to trash (False).
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The response from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    url = f"{base_url}/products/reviews/{review_id}"
    params = {'force': force}
    response = requests.delete(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_payment_gateways(site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/payment_gateways", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_payment_gateway(gateway_id: str, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/payment_gateways/{gateway_id}", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_payment_gateway(gateway_id: str, gateway_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Update a WooCommerce payment gateway.

    Args:
        gateway_id (str): The ID of the payment gateway to update (e.g., 'stripe', 'paypal').
        gateway_data (dict): Dictionary containing gateway configuration data. Possible fields:
            - enabled (bool): Whether the gateway is enabled
            - title (str): Gateway title
            - description (str): Gateway description
            - settings (dict): Gateway-specific settings
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The updated gateway configuration from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.put(f"{base_url}/payment_gateways/{gateway_id}", json=gateway_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_settings(site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    """
    Get all WooCommerce settings.

    Args:
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        list: List of all WooCommerce settings.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/settings", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_setting_options(group: str, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    """
    Get WooCommerce settings for a specific group.

    Args:
        group (str): The settings group to retrieve (e.g., 'general', 'products', 'shipping').
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        list: List of settings for the specified group.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/settings/{group}", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_setting_option(group: str, id: str, setting_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Update a specific WooCommerce setting option.

    Args:
        group (str): The settings group containing the option (e.g., 'general', 'products', 'shipping').
        id (str): The ID of the setting option to update.
        setting_data (dict): Dictionary containing the new setting value.
            - value: The new value for the setting.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The updated setting option from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.put(f"{base_url}/settings/{group}/{id}", json=setting_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_system_status(site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Get WooCommerce system status information.

    Args:
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: System status information including:
            - environment: WordPress and WooCommerce configuration
            - database: Database status and information
            - server: Server configuration and performance
            - tools: Available system tools
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/system_status", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_system_status_tools(site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    """
    Get available WooCommerce system tools.

    Args:
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        list: List of available system tools with their descriptions and usage information.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/system_status/tools", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def run_system_status_tool(tool_id: str, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Run a specific WooCommerce system tool.

    Args:
        tool_id (str): The ID of the tool to run (e.g., 'clear_transients', 'clear_cache').
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The result of running the system tool.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.post(f"{base_url}/system_status/tools/{tool_id}", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_data(site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/data", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_continents(site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/data/continents", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_countries(site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/data/countries", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_currencies(site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/data/currencies", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_current_currency(site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/data/currencies/current", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_sales_report(period: str = "month", date_min: str = "", date_max: str = "", site_url: str = "", consumer_key: str = "", consumer_secret: str = "", **filters) -> dict:
    """
    Get WooCommerce sales report data.

    Args:
        period (str): Time period for the report ('day', 'week', 'month', 'year').
        date_min (str): Start date for the report (YYYY-MM-DD).
        date_max (str): End date for the report (YYYY-MM-DD).
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.
        **filters: Additional filter parameters:
            - status (str): Order status filter
            - product_id (int): Filter by product ID
            - category_id (int): Filter by category ID
            - customer_id (int): Filter by customer ID

    Returns:
        dict: Sales report data including:
            - totals: Overall sales statistics
            - intervals: Time-based sales data
            - downloads: Downloadable product statistics
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'period': period, 'date_min': date_min, 'date_max': date_max}
    params.update(filters)
    response = requests.get(f"{base_url}/reports/sales", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_products_report(period: str = "month", date_min: str = "", date_max: str = "", per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "", **filters) -> dict:
    """
    Get WooCommerce product sales report.

    Args:
        period (str): Time period for the report ('day', 'week', 'month', 'year').
        date_min (str): Start date for the report (YYYY-MM-DD).
        date_max (str): End date for the report (YYYY-MM-DD).
        per_page (int): Number of items per page.
        page (int): Page number to retrieve.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.
        **filters: Additional filter parameters:
            - status (str): Order status filter
            - product_id (int): Filter by product ID
            - category_id (int): Filter by category ID
            - customer_id (int): Filter by customer ID

    Returns:
        dict: Product sales report data including:
            - products: List of products with sales data
            - totals: Overall product sales statistics
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'period': period, 'date_min': date_min, 'date_max': date_max, 'per_page': per_page, 'page': page}
    params.update(filters)
    response = requests.get(f"{base_url}/reports/products", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_orders_report(period: str = "month", date_min: str = "", date_max: str = "", per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "", **filters) -> dict:
    """
    Get WooCommerce orders report.

    Args:
        period (str): Time period for the report ('day', 'week', 'month', 'year').
        date_min (str): Start date for the report (YYYY-MM-DD).
        date_max (str): End date for the report (YYYY-MM-DD).
        per_page (int): Number of items per page.
        page (int): Page number to retrieve.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.
        **filters: Additional filter parameters:
            - status (str): Order status filter
            - product_id (int): Filter by product ID
            - category_id (int): Filter by category ID
            - customer_id (int): Filter by customer ID

    Returns:
        dict: Orders report data including:
            - orders: List of orders with detailed information
            - totals: Overall order statistics
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'period': period, 'date_min': date_min, 'date_max': date_max, 'per_page': per_page, 'page': page}
    params.update(filters)
    response = requests.get(f"{base_url}/reports/orders", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_categories_report(per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "", **filters) -> dict:
    """
    Get WooCommerce categories report.

    Args:
        per_page (int): Number of items per page.
        page (int): Page number to retrieve.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.
        **filters: Additional filter parameters:
            - product_id (int): Filter by product ID
            - category_id (int): Filter by category ID

    Returns:
        dict: Categories report data including:
            - categories: List of categories with sales data
            - totals: Overall category sales statistics
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'per_page': per_page, 'page': page}
    params.update(filters)
    response = requests.get(f"{base_url}/reports/categories", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_customers_report(per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "", **filters) -> dict:
    """
    Get WooCommerce customers report.

    Args:
        per_page (int): Number of items per page.
        page (int): Page number to retrieve.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.
        **filters: Additional filter parameters:
            - customer_id (int): Filter by customer ID
            - product_id (int): Filter by product ID
            - category_id (int): Filter by category ID

    Returns:
        dict: Customers report data including:
            - customers: List of customers with purchase history
            - totals: Overall customer statistics
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'per_page': per_page, 'page': page}
    params.update(filters)
    response = requests.get(f"{base_url}/reports/customers", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_stock_report(per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "", **filters) -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'per_page': per_page, 'page': page}
    params.update(filters)
    response = requests.get(f"{base_url}/reports/stock", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_coupons_report(period: str = "month", date_min: str = "", date_max: str = "", per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "", **filters) -> dict:
    """
    Get WooCommerce coupon usage report.

    Args:
        period (str): Time period for the report ('day', 'week', 'month', 'year').
        date_min (str): Start date for the report (YYYY-MM-DD).
        date_max (str): End date for the report (YYYY-MM-DD).
        per_page (int): Number of items per page.
        page (int): Page number to retrieve.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.
        **filters: Additional filter parameters:
            - coupon_id (int): Filter by coupon ID
            - status (str): Coupon status filter

    Returns:
        dict: Coupon usage report data including:
            - coupons: List of coupons with usage statistics
            - totals: Overall coupon usage statistics
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'period': period, 'date_min': date_min, 'date_max': date_max, 'per_page': per_page, 'page': page}
    params.update(filters)
    response = requests.get(f"{base_url}/reports/coupons/totals", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_taxes_report(period: str = "month", date_min: str = "", date_max: str = "", per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "", **filters) -> dict:
    """
    Get WooCommerce taxes report.

    Args:
        period (str): Time period for the report ('day', 'week', 'month', 'year').
        date_min (str): Start date for the report (YYYY-MM-DD).
        date_max (str): End date for the report (YYYY-MM-DD).
        per_page (int): Number of items per page.
        page (int): Page number to retrieve.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.
        **filters: Additional filter parameters:
            - tax_id (int): Filter by tax ID
            - country (str): Filter by country code
            - state (str): Filter by state code

    Returns:
        dict: Taxes report data including:
            - taxes: List of taxes with collection statistics
            - totals: Overall tax collection statistics
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'period': period, 'date_min': date_min, 'date_max': date_max, 'per_page': per_page, 'page': page}
    params.update(filters)
    response = requests.get(f"{base_url}/reports/taxes", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_coupons(per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    """
    Get a list of WooCommerce coupons.

    Args:
        per_page (int): Number of coupons per page.
        page (int): Page number to retrieve.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        list: List of coupon data dictionaries.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'per_page': per_page, 'page': page}
    response = requests.get(f"{base_url}/coupons", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_coupon(coupon_id: int, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Get a specific WooCommerce coupon.

    Args:
        coupon_id (int): The ID of the coupon to retrieve.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The coupon data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/coupons/{coupon_id}", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_coupon(coupon_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Create a new WooCommerce coupon.

    Args:
        coupon_data (dict): Dictionary containing coupon information. Required fields:
            - code (str): Coupon code
            - discount_type (str): Type of discount ('fixed_cart', 'percent', 'fixed_product', 'percent_product')
            - amount (str): Discount amount
            Optional fields:
            - description (str): Coupon description
            - date_expires (str): Expiration date (YYYY-MM-DD)
            - usage_limit (int): Usage limit per coupon
            - usage_limit_per_user (int): Usage limit per user
            - minimum_amount (float): Minimum cart amount
            - maximum_amount (float): Maximum cart amount
            - individual_use (bool): Whether the coupon can be used individually
            - exclude_sale_items (bool): Whether to exclude sale items
            - product_ids (list): List of product IDs to apply the coupon to
            - exclude_product_ids (list): List of product IDs to exclude
            - usage_count (int): Number of times the coupon has been used
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The created coupon data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.post(f"{base_url}/coupons", json=coupon_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def update_coupon(coupon_id: int, coupon_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Update an existing WooCommerce coupon.

    Args:
        coupon_id (int): The ID of the coupon to update.
        coupon_data (dict): Dictionary containing coupon information to update. Possible fields:
            - code (str): Coupon code
            - discount_type (str): Type of discount ('fixed_cart', 'percent', 'fixed_product', 'percent_product')
            - amount (str): Discount amount
            - description (str): Coupon description
            - date_expires (str): Expiration date (YYYY-MM-DD)
            - usage_limit (int): Usage limit per coupon
            - usage_limit_per_user (int): Usage limit per user
            - minimum_amount (float): Minimum cart amount
            - maximum_amount (float): Maximum cart amount
            - individual_use (bool): Whether the coupon can be used individually
            - exclude_sale_items (bool): Whether to exclude sale items
            - product_ids (list): List of product IDs to apply the coupon to
            - exclude_product_ids (list): List of product IDs to exclude
            - usage_count (int): Number of times the coupon has been used
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The updated coupon data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.put(f"{base_url}/coupons/{coupon_id}", json=coupon_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_coupon(coupon_id: int, force: bool = True, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'force': force}
    response = requests.delete(f"{base_url}/coupons/{coupon_id}", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

# --- Order Notes ---
@mcp.tool()
def get_order_notes(order_id: int, per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    """
    Get a list of notes for a WooCommerce order.

    Args:
        order_id (int): The ID of the order to retrieve notes for.
        per_page (int): Number of notes per page.
        page (int): Page number to retrieve.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        list: List of order note dictionaries.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'per_page': per_page, 'page': page}
    response = requests.get(f"{base_url}/orders/{order_id}/notes", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_order_note(order_id: int, note_id: int, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Get a specific order note.

    Args:
        order_id (int): The ID of the order containing the note.
        note_id (int): The ID of the note to retrieve.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The order note data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/orders/{order_id}/notes/{note_id}", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_order_note(order_id: int, note_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Create a new order note for a WooCommerce order.

    Args:
        order_id (int): The ID of the order to add the note to.
        note_data (dict): Dictionary containing note information. Required fields:
            - note (str): The note content
            - customer_note (bool): Whether this is a customer note (True) or internal note (False)
            Optional fields:
            - meta_data (list): List of meta data objects
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The created note data from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.post(f"{base_url}/orders/{order_id}/notes", json=note_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_order_note(order_id: int, note_id: int, force: bool = True, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    """
    Delete an order note from a WooCommerce order.

    Args:
        order_id (int): The ID of the order containing the note.
        note_id (int): The ID of the note to delete.
        force (bool): Whether to permanently delete the note (True) or move to trash (False).
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        dict: The response from the WooCommerce API.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'force': force}
    response = requests.delete(f"{base_url}/orders/{order_id}/notes/{note_id}", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

# --- Order Refunds ---
@mcp.tool()
def get_order_refunds(order_id: int, per_page: int = 10, page: int = 1, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'per_page': per_page, 'page': page}
    response = requests.get(f"{base_url}/orders/{order_id}/refunds", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def get_order_refund(order_id: int, refund_id: int, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/orders/{order_id}/refunds/{refund_id}", headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def create_order_refund(order_id: int, refund_data: dict, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.post(f"{base_url}/orders/{order_id}/refunds", json=refund_data, headers=headers)
    response.raise_for_status()
    return response.json()

@mcp.tool()
def delete_order_refund(order_id: int, refund_id: int, force: bool = True, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> dict:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    params = {'force': force}
    response = requests.delete(f"{base_url}/orders/{order_id}/refunds/{refund_id}", params=params, headers=headers)
    response.raise_for_status()
    return response.json()

# --- Meta operations for products ---
@mcp.tool()
def get_product_meta(product_id: int, meta_key: str = None, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/products/{product_id}", headers=headers)
    response.raise_for_status()
    meta_data = response.json().get('meta_data', [])
    if meta_key:
        return [meta for meta in meta_data if meta.get('key') == meta_key]
    return meta_data

@mcp.tool()
def update_product_meta(product_id: int, meta_key: str, meta_value, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    product = requests.get(f"{base_url}/products/{product_id}", headers=headers).json()
    meta_data = product.get('meta_data', [])
    found = False
    for meta in meta_data:
        if meta.get('key') == meta_key:
            meta['value'] = meta_value
            found = True
            break
    if not found:
        meta_data.append({'key': meta_key, 'value': meta_value})
    response = requests.put(f"{base_url}/products/{product_id}", json={'meta_data': meta_data}, headers=headers)
    response.raise_for_status()
    return response.json().get('meta_data', [])

@mcp.tool()
def create_product_meta(product_id: int, meta_key: str, meta_value, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    return update_product_meta(product_id, meta_key, meta_value, site_url, consumer_key, consumer_secret)

@mcp.tool()
def delete_product_meta(product_id: int, meta_key: str, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    product = requests.get(f"{base_url}/products/{product_id}", headers=headers).json()
    meta_data = product.get('meta_data', [])
    meta_data = [meta for meta in meta_data if meta.get('key') != meta_key]
    response = requests.put(f"{base_url}/products/{product_id}", json={'meta_data': meta_data}, headers=headers)
    response.raise_for_status()
    return response.json().get('meta_data', [])

# --- Meta operations for orders ---
@mcp.tool()
def get_order_meta(order_id: int, meta_key: str = None, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    """
    Get meta data for a WooCommerce order.

    Args:
        order_id (int): The ID of the order to retrieve meta data for.
        meta_key (str, optional): Specific meta key to filter by. If None, returns all meta data.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        list: List of meta data dictionaries. Each dictionary contains:
            - id (int): Meta ID
            - key (str): Meta key
            - value: Meta value (can be any type)
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/orders/{order_id}", headers=headers)
    response.raise_for_status()
    meta_data = response.json().get('meta_data', [])
    if meta_key:
        return [meta for meta in meta_data if meta.get('key') == meta_key]
    return meta_data

@mcp.tool()
def update_order_meta(order_id: int, meta_key: str, meta_value, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    """
    Update meta data for a WooCommerce order.

    Args:
        order_id (int): The ID of the order to update meta data for.
        meta_key (str): The meta key to update.
        meta_value: The new value for the meta key. Can be any JSON-serializable value.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        list: Updated list of meta data dictionaries for the order.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    order = requests.get(f"{base_url}/orders/{order_id}", headers=headers).json()
    meta_data = order.get('meta_data', [])
    found = False
    for meta in meta_data:
        if meta.get('key') == meta_key:
            meta['value'] = meta_value
            found = True
            break
    if not found:
        meta_data.append({'key': meta_key, 'value': meta_value})
    response = requests.put(f"{base_url}/orders/{order_id}", json={'meta_data': meta_data}, headers=headers)
    response.raise_for_status()
    return response.json().get('meta_data', [])

@mcp.tool()
def create_order_meta(order_id: int, meta_key: str, meta_value, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    """
    Create new meta data for a WooCommerce order.

    Args:
        order_id (int): The ID of the order to add meta data to.
        meta_key (str): The meta key to create.
        meta_value: The value for the new meta key. Can be any JSON-serializable value.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        list: Updated list of meta data dictionaries for the order.
    """
    return update_order_meta(order_id, meta_key, meta_value, site_url, consumer_key, consumer_secret)

@mcp.tool()
def delete_order_meta(order_id: int, meta_key: str, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    """
    Delete meta data from a WooCommerce order.

    Args:
        order_id (int): The ID of the order to delete meta data from.
        meta_key (str): The meta key to delete.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        list: Updated list of meta data dictionaries for the order.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    order = requests.get(f"{base_url}/orders/{order_id}", headers=headers).json()
    meta_data = order.get('meta_data', [])
    meta_data = [meta for meta in meta_data if meta.get('key') != meta_key]
    response = requests.put(f"{base_url}/orders/{order_id}", json={'meta_data': meta_data}, headers=headers)
    response.raise_for_status()
    return response.json().get('meta_data', [])

# --- Meta operations for customers ---
@mcp.tool()
def get_customer_meta(customer_id: int, meta_key: str = None, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    """
    Get meta data for a WooCommerce customer.

    Args:
        customer_id (int): The ID of the customer to retrieve meta data for.
        meta_key (str, optional): Specific meta key to filter by. If None, returns all meta data.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        list: List of meta data dictionaries. Each dictionary contains:
            - id (int): Meta ID
            - key (str): Meta key
            - value: Meta value (can be any type)
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    response = requests.get(f"{base_url}/customers/{customer_id}", headers=headers)
    response.raise_for_status()
    meta_data = response.json().get('meta_data', [])
    if meta_key:
        return [meta for meta in meta_data if meta.get('key') == meta_key]
    return meta_data

@mcp.tool()
def update_customer_meta(customer_id: int, meta_key: str, meta_value, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    """
    Update meta data for a WooCommerce customer.

    Args:
        customer_id (int): The ID of the customer to update meta data for.
        meta_key (str): The meta key to update.
        meta_value: The new value for the meta key. Can be any JSON-serializable value.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        list: Updated list of meta data dictionaries for the customer.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    customer = requests.get(f"{base_url}/customers/{customer_id}", headers=headers).json()
    meta_data = customer.get('meta_data', [])
    found = False
    for meta in meta_data:
        if meta.get('key') == meta_key:
            meta['value'] = meta_value
            found = True
            break
    if not found:
        meta_data.append({'key': meta_key, 'value': meta_value})
    response = requests.put(f"{base_url}/customers/{customer_id}", json={'meta_data': meta_data}, headers=headers)
    response.raise_for_status()
    return response.json().get('meta_data', [])

@mcp.tool()
def create_customer_meta(customer_id: int, meta_key: str, meta_value, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    """
    Create new meta data for a WooCommerce customer.

    Args:
        customer_id (int): The ID of the customer to add meta data to.
        meta_key (str): The meta key to create.
        meta_value: The value for the new meta key. Can be any JSON-serializable value.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        list: Updated list of meta data dictionaries for the customer.
    """
    return update_customer_meta(customer_id, meta_key, meta_value, site_url, consumer_key, consumer_secret)

@mcp.tool()
def delete_customer_meta(customer_id: int, meta_key: str, site_url: str = "", consumer_key: str = "", consumer_secret: str = "") -> list:
    """
    Delete meta data from a WooCommerce customer.

    Args:
        customer_id (int): The ID of the customer to delete meta data from.
        meta_key (str): The meta key to delete.
        site_url (str): The base URL of the WooCommerce site.
        consumer_key (str): The WooCommerce REST API consumer key.
        consumer_secret (str): The WooCommerce REST API consumer secret.

    Returns:
        list: Updated list of meta data dictionaries for the customer.
    """
    base_url, headers = get_woo_client(site_url, consumer_key, consumer_secret)
    customer = requests.get(f"{base_url}/customers/{customer_id}", headers=headers).json()
    meta_data = customer.get('meta_data', [])
    meta_data = [meta for meta in meta_data if meta.get('key') != meta_key]
    response = requests.put(f"{base_url}/customers/{customer_id}", json={'meta_data': meta_data}, headers=headers)
    response.raise_for_status()
    return response.json().get('meta_data', [])

if __name__ == "__main__":
   print("WordPress MCP Server is Running")
   mcp.run(transport="stdio")

