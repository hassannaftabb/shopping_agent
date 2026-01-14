from __future__ import annotations

import json
import os
import random
import smtplib
import uuid
from email.mime.text import MIMEText
from typing import Any, Dict

from livekit.agents import RunContext, function_tool

from .session import DataKey, SessionManager

_otp_storage: Dict[str, str] = {}


def build_data_collection_schema() -> Dict[str, Any]:
    """Build schema for data collection tool."""
    return {
        "name": "collect_data",
        "description": "Call this tool whenever you extract key information from the conversation. When the call is complete and you've said goodbye, call this with summary to finalize the call.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                    "description": "Customer's name",
                    "default": ""
                },
                "product_selection": {
                    "type": "string",
                    "description": "Product selected by customer",
                    "default": ""
                },
                "email": {
                    "type": "string",
                    "description": "Customer's email address",
                    "default": ""
                },
                "script_stage": {
                    "type": "string",
                    "description": "Current stage of the script",
                    "enum": ["intro", "needs_assessment", "product_selection", "email_collection", "otp_verification", "order_confirmation", "closing"],
                    "default": ""
                },
                "summary": {
                    "type": "string",
                    "description": "Final summary of the call (only provide when call is complete and you've said goodbye)",
                    "default": ""
                }
            },
            "required": [],
            "additionalProperties": False,
        },
    }


def build_get_product_options_schema() -> Dict[str, Any]:
    """Build schema for get_product_options tool."""
    return {
        "name": "get_product_options",
        "description": "Retrieve product options for a given category (Hoodie, T-Shirt, or Jacket)",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Product category: Hoodie, T-Shirt, or Jacket",
                    "enum": ["Hoodie", "T-Shirt", "Jacket"],
                }
            },
            "required": ["category"],
            "additionalProperties": False,
        },
    }


def build_send_otp_schema() -> Dict[str, Any]:
    """Build schema for send_otp tool."""
    return {
        "name": "send_otp",
        "description": "Send OTP verification code to customer's email address",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Customer's email address",
                }
            },
            "required": ["email"],
            "additionalProperties": False,
        },
    }


def build_verify_otp_schema() -> Dict[str, Any]:
    """Build schema for verify_otp tool."""
    return {
        "name": "verify_otp",
        "description": "Verify the OTP code provided by customer",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Customer's email address",
                },
                "otp_code": {
                    "type": "string",
                    "description": "OTP code provided by customer",
                }
            },
            "required": ["email", "otp_code"],
            "additionalProperties": False,
        },
    }


def build_generate_order_schema() -> Dict[str, Any]:
    """Build schema for generate_order tool."""
    return {
        "name": "generate_order",
        "description": "Generate order ID and tracking ID, then save order to Excel/CSV",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                    "description": "Customer's name",
                },
                "product": {
                    "type": "string",
                    "description": "Product name selected by customer",
                },
                "email": {
                    "type": "string",
                    "description": "Customer's email address",
                }
            },
            "required": ["customer_name", "product", "email"],
            "additionalProperties": False,
        },
    }


def create_data_collection_tool(session_manager: SessionManager) -> Any:
    """Create data collection tool for tracking conversation data."""
    schema = build_data_collection_schema()

    @function_tool(raw_schema=schema)
    async def collect_data_handler(raw_arguments: Dict[str, Any], context: RunContext) -> str:
        """Handle data collection during conversation."""
        try:
            customer_name = str(raw_arguments.get("customer_name", "")).strip()
            product_selection = str(raw_arguments.get("product_selection", "")).strip()
            email = str(raw_arguments.get("email", "")).strip()
            script_stage = str(raw_arguments.get("script_stage", "")).strip()
            summary = str(raw_arguments.get("summary", "")).strip()

            if customer_name:
                session_manager.update_data(DataKey.CUSTOMER_NAME, customer_name)
            
            if product_selection:
                session_manager.update_data(DataKey.PRODUCT_SELECTION, product_selection)
            
            if email:
                session_manager.update_data(DataKey.EMAIL, email)
            
            if script_stage:
                session_manager.update_data(DataKey.SCRIPT_STAGE, script_stage)
            
            if summary:
                session_manager.update_data(DataKey.SUMMARY, summary)
                return None

            return "Data collected successfully"

        except Exception as e:
            print(f"Error collecting data: {e}")
            return f"Error collecting data: {str(e)}"

    return collect_data_handler


def create_get_product_options_tool() -> Any:
    """Create tool to retrieve product options from inventory."""
    schema = build_get_product_options_schema()

    @function_tool(raw_schema=schema)
    async def get_product_options_handler(raw_arguments: Dict[str, Any], context: RunContext) -> str:
        """Retrieve product options for a category."""
        try:
            category = raw_arguments.get("category", "").strip()
            
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            inventory_path = os.path.join(project_root, "inventory.json")
            
            if not os.path.exists(inventory_path):
                return f"Error: Inventory file not found at {inventory_path}"
            
            with open(inventory_path, "r", encoding="utf-8") as f:
                inventory = json.load(f)
            
            products = inventory.get("products", {}).get(category, [])
            
            if not products:
                return f"No products found for category: {category}"
            
            product_list = []
            for i, product in enumerate(products, 1):
                price_str = ""
                if product.get('price'):
                    price_str = f" - PKR {product['price']:,}"
                else:
                    price_str = " - Price on request"
                product_list.append(f"Option {i}: {product['name']} - {product['description']}{price_str}")
            
            result = f"Based on our latest collection, I have {len(products)} top recommendations for you:\n\n" + "\n\n".join(product_list) + "\n\nAll prices are in PKR (Pakistani Rupees)."
            
            return result

        except Exception as e:
            print(f"Error retrieving products: {e}")
            return f"Error retrieving products: {str(e)}"

    return get_product_options_handler


def _send_email_otp(email: str, otp_code: str) -> bool:
    """Send OTP code via email using SMTP."""
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        from_email = os.getenv("FROM_EMAIL", smtp_username)
        
        if not smtp_username or not smtp_password:
            print("SMTP credentials not configured. OTP will be stored but not sent via email.")
            print(f"   OTP for {email}: {otp_code}")
            return False
        
        msg = MIMEText(f"Your Zenitheon verification code is: {otp_code}\n\nThis code will expire in 10 minutes.")
        msg["Subject"] = "Zenitheon Order Verification Code"
        msg["From"] = from_email
        msg["To"] = email
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print(f"OTP sent to {email}")
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        print(f"   OTP for {email}: {otp_code} (stored in memory)")
        return False


def _send_order_confirmation_email(email: str, customer_name: str, product: str, order_id: str, tracking_id: str) -> bool:
    """Send order confirmation email with tracking ID and order ID."""
    try:
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        from_email = os.getenv("FROM_EMAIL", smtp_username)
        
        if not smtp_username or not smtp_password:
            print("SMTP credentials not configured. Order confirmation email not sent.")
            print(f"   Order confirmation for {email}:")
            print(f"   Order ID: {order_id}")
            print(f"   Tracking ID: {tracking_id}")
            return False
        
        email_body = f"""Dear {customer_name},

Thank you for your order with Zenitheon!

Order Details:
- Product: {product}
- Order ID: {order_id}
- Tracking ID: {tracking_id}

Your order has been confirmed and will be processed shortly.

Thank you for shopping with Zenitheon. Have a stylish day!

Best regards,
Zenitheon Team
"""
        
        msg = MIMEText(email_body)
        msg["Subject"] = f"Zenitheon Order Confirmation - {order_id}"
        msg["From"] = from_email
        msg["To"] = email
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print(f"Order confirmation email sent to {email}")
        return True
        
    except Exception as e:
        print(f"Error sending order confirmation email: {e}")
        print(f"   Order confirmation for {email}:")
        print(f"   Order ID: {order_id}")
        print(f"   Tracking ID: {tracking_id}")
        return False


def create_send_otp_tool() -> Any:
    """Create tool to send OTP to customer's email."""
    schema = build_send_otp_schema()

    @function_tool(raw_schema=schema)
    async def send_otp_handler(raw_arguments: Dict[str, Any], context: RunContext) -> str:
        """Send OTP code to customer's email."""
        try:
            email = raw_arguments.get("email", "").strip().lower()
            
            if not email:
                return "Error: Email address is required"
            
            otp_code = str(random.randint(100000, 999999))
            
            _otp_storage[email] = otp_code
            
            _send_email_otp(email, otp_code)
            
            return f"OTP code sent to {email}"

        except Exception as e:
            print(f"Error sending OTP: {e}")
            return f"Error sending OTP: {str(e)}"

    return send_otp_handler


def create_verify_otp_tool() -> Any:
    """Create tool to verify OTP code."""
    schema = build_verify_otp_schema()

    @function_tool(raw_schema=schema)
    async def verify_otp_handler(raw_arguments: Dict[str, Any], context: RunContext) -> str:
        """Verify OTP code provided by customer."""
        try:
            email = raw_arguments.get("email", "").strip().lower()
            otp_code = raw_arguments.get("otp_code", "").strip()
            
            if not email or not otp_code:
                return "Error: Email and OTP code are required"
            
            stored_otp = _otp_storage.get(email)
            
            if not stored_otp:
                return "Error: No OTP found for this email. Please request a new OTP."
            
            if stored_otp != otp_code:
                return "Error: Invalid OTP code. Please try again."
            
            del _otp_storage[email]
            
            return "OTP verified successfully"

        except Exception as e:
            print(f"Error verifying OTP: {e}")
            return f"Error verifying OTP: {str(e)}"

    return verify_otp_handler


def create_generate_order_tool(session_manager: SessionManager) -> Any:
    """Create tool to generate order ID and save to Excel/CSV."""
    schema = build_generate_order_schema()

    @function_tool(raw_schema=schema)
    async def generate_order_handler(raw_arguments: Dict[str, Any], context: RunContext) -> str:
        """Generate order ID and tracking ID, then save order."""
        try:
            customer_name = raw_arguments.get("customer_name", "").strip()
            product = raw_arguments.get("product", "").strip()
            email = raw_arguments.get("email", "").strip()
            
            if not customer_name or not product or not email:
                return "Error: Customer name, product, and email are required"
            
            session_manager.update_data(DataKey.CUSTOMER_NAME, customer_name)
            session_manager.update_data(DataKey.PRODUCT_SELECTION, product)
            session_manager.update_data(DataKey.EMAIL, email)
            
            order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            tracking_id = f"TRK-{uuid.uuid4().hex[:12].upper()}"
            
            result = session_manager.save_order_data(order_id, tracking_id)
            
            if result:
                _send_order_confirmation_email(email, customer_name, product, order_id, tracking_id)
                return f"Order generated successfully. Order ID: {order_id}, Tracking ID: {tracking_id}"
            else:
                return f"Error: Failed to save order data"

        except Exception as e:
            print(f"Error generating order: {e}")
            return f"Error generating order: {str(e)}"

    return generate_order_handler
