from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ScriptVariables:
    """Configuration variables for the recruitment script."""
    
    # Company details
    company_name: str = "Ultimate Outsourcing"
    recruiter_name: str = "Morgan"
    recruiter_title: str = "Recruitment Consultant"
    
    candidate_name: str = "John"
    
    # Job details - these can be customized per call
    role: str = "Software Developer"
    industry: str = "Technology"
    location: str = "Remote"
    salary: str = "$80,000 to $120,000"
    
    # Call flow customization
    intro_greeting: str = f"Hi, {candidate_name}, this is {recruiter_name}, {recruiter_title} calling from {company_name}. Is it a good time to talk?"
    reason_for_call: str = f"We're recruiting for a {role} {industry} in {location}, offering {salary}. Are you open to exploring this opportunity?"
    
    # Decline handling
    decline_question: str = f"I completely understand, {candidate_name}. Is it salary, location, timing, or something else?"
    decline_with_reason: str = "Got it, thanks for sharing. I can pass your details to our Senior Consultant if something closer comes up. Thanks for your time. Bye."
    decline_no_reason: str = f"No problem at all—thank you for your time today, {candidate_name}. Wishing you all the best. Goodbye."
        
    # Closing responses
    engaged_closing: str = f"Perfect, {candidate_name}. You'll hear from our Senior Consultant shortly. Thanks for your time today. Goodbye."
    not_interested_closing: str = f"Understood, {candidate_name}. Thanks again for your time—wishing you all the best. Goodbye."


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
        recruiter_name=kwargs.get('recruiter_name', current_vars.recruiter_name),
        recruiter_title=kwargs.get('recruiter_title', current_vars.recruiter_title),
        role=kwargs.get('role', current_vars.role),
        industry=kwargs.get('industry', current_vars.industry),
        location=kwargs.get('location', current_vars.location),
        salary=kwargs.get('salary', current_vars.salary),
        intro_greeting=kwargs.get('intro_greeting', current_vars.intro_greeting),
        reason_for_call=kwargs.get('reason_for_call', current_vars.reason_for_call),
        decline_question=kwargs.get('decline_question', current_vars.decline_question),
        decline_with_reason=kwargs.get('decline_with_reason', current_vars.decline_with_reason),
        decline_no_reason=kwargs.get('decline_no_reason', current_vars.decline_no_reason),
        engaged_closing=kwargs.get('engaged_closing', current_vars.engaged_closing),
        not_interested_closing=kwargs.get('not_interested_closing', current_vars.not_interested_closing),
    )
    DEFAULT_SCRIPT_VARS = updated_vars
    return updated_vars
