[
  {
    "name": "initiate_refund",
    "description": "Initiate a refund for a customer order.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "reason": {
          "type": "string",
          "description": "Reason for refund"
        },
        "amount": {
          "type": "number",
          "description": "Refund amount in USD"
        },
        "order_id": {
          "type": "string",
          "description": "Order ID to refund"
        }
      },
      "required": [
        "order_id",
        "reason"
      ]
    }
  },
  {
    "name": "check_refund_status",
    "description": "Check the status of an existing refund.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "refund_id": {
          "type": "string",
          "description": "Refund ID to check"
        }
      },
      "required": [
        "refund_id"
      ]
    }
  },
  {
    "name": "get_return_label",
    "description": "Generate a prepaid return shipping label for an order.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "order_id": {
          "type": "string",
          "description": "Order ID needing a label"
        }
      },
      "required": [
        "order_id"
      ]
    }
  }
]