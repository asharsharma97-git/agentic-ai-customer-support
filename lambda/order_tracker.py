"""
Order Tracking Lambda
======================
Handles order and customer lookup.
Invoked through the AgentCore Gateway (REST API proxy integration).

Routes exposed:
  GET /orders/{order_id}              — return a single order by ID
  GET /customers/{customer_id}/orders — return all orders for a customer
  GET /customers/{customer_id}        — return customer profile

The data is hard-coded for demonstration purposes.  In a real system these
handlers would query a database such as Amazon DynamoDB.

Deployment: zip this file and upload to an AWS Lambda function, then wire
the function to the AgentCore Gateway as a target using API Gateway proxy
integration.
"""
import json
from datetime import datetime, timedelta


# ── Sample data ───────────────────────────────────────────────────────────────
# Returned as a fresh dict on every call so state is never shared across
# Lambda invocations (relevant when the execution environment is reused).

def _orders():
    """Return the mock order database."""
    return {
        "ORD-001": {
            "order_id":          "ORD-001",
            "customer_id":       "CUST-123",
            "status":            "SHIPPED",
            "items":             [{"name": "Wireless Headphones Pro", "qty": 1, "price": 89.99}],
            "total":             89.99,
            "tracking_number":   "TRK987654321",
            "carrier":           "UPS",
            # Delivery expected in 2 days from the time the Lambda runs.
            "estimated_delivery": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        },
        "ORD-002": {
            "order_id":     "ORD-002",
            "customer_id":  "CUST-123",
            "status":       "DELIVERED",
            "items":        [{"name": "Kindle Paperwhite", "qty": 1, "price": 139.99}],
            "total":        139.99,
            "tracking_number": "TRK123456789",
            "carrier":      "USPS",
            # Delivered 3 days ago.
            "delivered_date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        },
        "ORD-003": {
            "order_id":     "ORD-003",
            "customer_id":  "CUST-456",
            "status":       "PROCESSING",
            "items": [
                {"name": "Echo Dot 5th Gen", "qty": 2, "price": 49.99},
                {"name": "Smart Plug",        "qty": 1, "price": 24.99},
            ],
            "total":              124.97,
            "estimated_delivery": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        },
    }


def _customers():
    """Return the mock customer database."""
    return {
        "CUST-123": {"name": "Jane Smith",  "loyalty_points": 4250, "tier": "Gold"},
        "CUST-456": {"name": "Bob Johnson", "loyalty_points": 890,  "tier": "Silver"},
    }


# ── Response helper ───────────────────────────────────────────────────────────
def _response(status_code: int, body: dict) -> dict:
    """
    Format a Lambda proxy-integration response.

    API Gateway requires a specific shape: statusCode, headers, and a
    JSON-serialised body string.
    """
    return {
        "statusCode": status_code,
        "headers":    {"Content-Type": "application/json"},
        "body":       json.dumps(body),
    }


# ── Handler ───────────────────────────────────────────────────────────────────
def lambda_handler(event, context):
    """
    Main Lambda entry point.

    The API Gateway REST proxy integration populates these event fields:
      resource       — the path template, e.g. /orders/{order_id}
      httpMethod     — GET, POST, etc.
      pathParameters — dict of path variable values, e.g. {"order_id": "ORD-001"}
    """
    print(f"Event: {json.dumps(event)}")

    # Extract routing fields from the proxy integration event.
    resource = event.get("resource", "")        # e.g. "/orders/{order_id}"
    method   = event.get("httpMethod", "GET")
    params   = event.get("pathParameters") or {}

    print(f"Request: {method} {resource} {params}")

    orders    = _orders()
    customers = _customers()

    # ── GET /orders/{order_id} ────────────────────────────────────────────────
    if resource == "/orders/{order_id}" and method == "GET":
        # Normalise to uppercase so "ord-001" and "ORD-001" both work.
        order_id = params.get("order_id", "").upper()
        order    = orders.get(order_id)
        if not order:
            return _response(404, {"error": f"Order {order_id} not found"})
        return _response(200, order)

    # ── GET /customers/{customer_id}/orders ───────────────────────────────────
    if resource == "/customers/{customer_id}/orders" and method == "GET":
        cid    = params.get("customer_id", "").upper()
        # Filter orders to only those belonging to the requested customer.
        result = [o for o in orders.values() if o["customer_id"] == cid]
        if not result:
            return _response(404, {"error": f"No orders found for {cid}"})
        return _response(200, {"customer_id": cid, "orders": result})

    # ── GET /customers/{customer_id} ──────────────────────────────────────────
    if resource == "/customers/{customer_id}" and method == "GET":
        cid      = params.get("customer_id", "").upper()
        customer = customers.get(cid)
        if not customer:
            return _response(404, {"error": f"Customer {cid} not found"})
        return _response(200, customer)

    # ── Unrecognised route ────────────────────────────────────────────────────
    return _response(400, {"error": "Unrecognised route", "resource": resource})
