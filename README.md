# WooCommerce API Integration Server

A Python server that provides a comprehensive interface for interacting with WooCommerce stores through their REST API.

## Features

- **Product Management**
  - Create, update, and delete products
  - Manage product categories
  - Handle product variations and attributes
  - Manage product tags

- **Customer Management**
  - Create, update, and delete customers
  - Manage customer meta data
  - Handle customer billing and shipping addresses

- **Order Management**
  - Create, update, and delete orders
  - Manage order notes
  - Handle order meta data
  - Process order line items and variations

- **Payment and Shipping**
  - Manage payment gateways
  - Handle shipping methods
  - Process order payments

- **Reports and Analytics**
  - Generate sales reports
  - Get product performance reports
  - View customer analytics
  - Track coupon usage

## Requirements

- Python 3.8+
- WooCommerce REST API
- JWT Authentication (optional)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd mcp-server-wordpress
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export WORDPRESS_SITE_URL="your-site-url"
export WORDPRESS_JWT_TOKEN="your-jwt-token"
export WOCOMMERCE_CONSUMER_KEY="your-consumer-key"
export WOCOMMERCE_CONSUMER_SECRET="your-consumer-secret"
```

## Usage

The server provides a set of tools that can be used to interact with WooCommerce stores. Here are some examples:

### Creating a Product
```python
product_data = {
    "name": "New Product",
    "type": "simple",
    "regular_price": "19.99",
    "description": "Product description",
    "short_description": "Short description",
    "categories": [{"id": 12}],
    "images": [{"src": "https://example.com/product-image.jpg"}]
}

create_product(product_data)
```

### Creating an Order
```python
order_data = {
    "payment_details": {
        "method_id": "bacs",
        "method_title": "Direct Bank Transfer",
        "paid": True
    },
    "billing_address": {
        "first_name": "John",
        "last_name": "Doe",
        "address_1": "969 Market",
        "city": "San Francisco",
        "state": "CA",
        "postcode": "94103",
        "country": "US",
        "email": "john.doe@example.com",
        "phone": "(555) 555-5555"
    },
    "line_items": [
        {
            "product_id": 546,
            "quantity": 2
        }
    ]
}

create_order(order_data)
```

## API Documentation

All available API functions are documented within the code using docstrings. Each function includes:
- Detailed parameter descriptions
- Required and optional fields
- Return value information
- Authentication requirements

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Developed By

- **Company Name**: Pardeep Kumar Freelancer
- **Website**: https://pardeep889.com/
- **GitHub**: https://github.com/pardeep889/
- **Upwork**: https://www.upwork.com/freelancers/~01bce18028157bd68a

