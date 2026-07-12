import os
import json
from google import genai
from pydantic import BaseModel

# We keep Pydantic for cleanly parsing the JSON response at the end
class ActionItem(BaseModel):
    event_date: str
    child_name: str
    summary: str
    required_action: str
    source_sender: str
    email_date: str 

class SchoolDigest(BaseModel):
    has_action_items: bool
    action_items: list[ActionItem]
    general_summary: str

def analyze_emails(emails: list[dict]) -> SchoolDigest:
    """Sends emails to Gemini and returns a structured Pydantic model."""
    client = genai.Client(vertexai=True, project=os.environ.get("GCP_PROJECT_ID"), location="us-central1")
    
    school_name = os.environ.get("SCHOOL_NAME", "their school")
    childcare_name = os.environ.get("CHILDCARE_NAME", "their childcare center")
    
    email_text_block = json.dumps(emails, indent=2)
    
    prompt = f"""
    You are an executive assistant for a parent. Review the following emails.
    Extract critical action items requiring parental preparation (e.g., dress up days, volunteer requests, signing forms, field trips) for their two children. 
    
    Pay special attention to emails and events concerning these specific institutions:
    - School: {school_name}
    - Childcare Center: {childcare_name}
    
    Ignore standard newsletters, marketing, or general updates that don't contain deadline-driven requirements. 
    Disregard events that occurred in the past relative to today.

    For each action item, also extract the original sender and the date the email was received. 
    Format the email date into a clean, readable format (e.g., 'Oct 24').
    
    Here are the emails:
    {email_text_block}
    """
    
    # Manually define the unrolled schema to bypass the Vertex AI $defs validation bug
    unrolled_schema = {
        "type": "OBJECT",
        "properties": {
            "has_action_items": {"type": "BOOLEAN"},
            "general_summary": {
                "type": "STRING", 
                "description": "A 2-3 sentence summary of the general news."
            },
            "action_items": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "event_date": {"type": "STRING", "description": "Date of the event or deadline."},
                        "child_name": {"type": "STRING", "description": "The name of the child this pertains to."},
                        "summary": {"type": "STRING", "description": "A brief description of the event."},
                        "required_action": {"type": "STRING", "description": "Exactly what the parent needs to do."},
                        "source_sender": {"type": "STRING", "description": "Who sent the original email."}, # NEW
                        "email_date": {"type": "STRING", "description": "When the email was received."}   # NEW
                    },
                    "required": ["event_date", "child_name", "summary", "required_action", "source_sender", "email_date"]
                }
            }
        },
        "required": ["has_action_items", "general_summary", "action_items"]
    }
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': unrolled_schema,
            'temperature': 0.1, 
        },
    )
    
    # Parse the returned JSON string back into our strongly-typed Pydantic model
    return SchoolDigest.model_validate_json(response.text)