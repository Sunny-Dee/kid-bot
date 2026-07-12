import os
import json
from google import genai
from pydantic import BaseModel, Field

class ActionItem(BaseModel):
    event_date: str = Field(description="The date the event or deadline occurs.")
    child_name: str = Field(description="The name of the child this pertains to, if specified.")
    summary: str = Field(description="A brief description of the event.")
    required_action: str = Field(description="Exactly what the parent needs to do (e.g., 'Pack a lunch', 'Dress in pajamas').")

class SchoolDigest(BaseModel):
    has_action_items: bool
    action_items: list[ActionItem]
    general_summary: str = Field(description="A 2-3 sentence summary of the general news.")

def analyze_emails(emails: list[dict]) -> SchoolDigest:
    """Sends emails to Gemini and returns a structured Pydantic model."""
    client = genai.Client(project=os.environ.get("GCP_PROJECT_ID"), location="us-central1")
    
    # 1. Pull the specific names from the environment
    # Using a fallback string just in case the variable is missing
    school_name = os.environ.get("SCHOOL_NAME", "their schools")
    childcare_name = os.environ.get("CHILDCARE_NAME", "their childcare center")
    
    email_text_block = json.dumps(emails, indent=2)
    
    # 2. Inject the variables directly into the f-string prompt
    prompt = f"""
    You are an executive assistant for a parent. Review the following emails.
    Extract critical action items requiring parental preparation (e.g., dress up days, volunteer requests, signing forms, field trips) for their two children. 
    
    Pay special attention to emails and events concerning these specific institutions:
    - Schools: {school_name}
    - Childcare Center: {childcare_name}
    
    Ignore standard newsletters, marketing, or general updates that don't contain deadline-driven family impacts. 
    Disregard events that occurred in the past relative to today.
    
    Here are the emails:
    {email_text_block}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': SchoolDigest,
            'temperature': 0.1, 
        },
    )
    
    return SchoolDigest.model_validate_json(response.text)