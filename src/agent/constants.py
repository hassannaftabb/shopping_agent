from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScriptVariables:
    """Configuration variables for the Zenitheon Shop Whisper ecommerce script."""
    
    # Company details
    company_name: str = "Zenitheon"
    agent_name: str = "Zen"
    agent_title: str = "personal AI shopping assistant"
    
    customer_name: str = ""
    
    # Call flow customization
    intro_greeting: str = "Welcome to Zenitheon. I am Zen, your personal AI shopping assistant. May I know who I am speaking with today?"
    needs_assessment: str = "It is a pleasure to meet you, {customer_name}. How can I help you upgrade your wardrobe today? Are you looking for something specific?"
    product_selection_prompt: str = "Which one of these catches your eye?"
    email_request: str = "Great selection. The {product_name} is a favorite. To finalize your order and send you the generated Tracking ID, could you please share your email address?"
    otp_request: str = "Thank you. I have sent a verification code to your email. Please provide the code to confirm your order."
    order_confirmation: str = "Thank you. I have confirmed your order. A confirmation email with your unique Tracking ID has just been sent to {email}. Thank you for shopping with Zenitheon. Have a stylish day!"


DEFAULT_SCRIPT_VARS = ScriptVariables()


def get_script_variables() -> ScriptVariables:
    """Get the current script variables configuration."""
    return DEFAULT_SCRIPT_VARS


def update_script_variables(**kwargs) -> ScriptVariables:
    """Update script variables with new values."""
    global DEFAULT_SCRIPT_VARS
    current_vars = DEFAULT_SCRIPT_VARS
    updated_vars = ScriptVariables(
        company_name=kwargs.get('company_name', current_vars.company_name),
        agent_name=kwargs.get('agent_name', current_vars.agent_name),
        agent_title=kwargs.get('agent_title', current_vars.agent_title),
        customer_name=kwargs.get('customer_name', current_vars.customer_name),
        intro_greeting=kwargs.get('intro_greeting', current_vars.intro_greeting),
        needs_assessment=kwargs.get('needs_assessment', current_vars.needs_assessment),
        product_selection_prompt=kwargs.get('product_selection_prompt', current_vars.product_selection_prompt),
        email_request=kwargs.get('email_request', current_vars.email_request),
        otp_request=kwargs.get('otp_request', current_vars.otp_request),
        order_confirmation=kwargs.get('order_confirmation', current_vars.order_confirmation),
    )
    DEFAULT_SCRIPT_VARS = updated_vars
    return updated_vars
