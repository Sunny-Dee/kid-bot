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
    child_name_1 = os.environ.get("CHILD_NAME_1", "Child 1")
    child_name_2 = os.environ.get("CHILD_NAME_2", "Child 2")
    childcare_level = os.environ.get("CHILDCARE_LEVEL", "")
    grade = os.environ.get("KIDS_GRADE", "")
    
    email_text_block = json.dumps(emails, indent=2)
    
    prompt = f"""
    You are an executive assistant for a parent. Review the following emails.
    Extract critical action items requiring parental preparation (e.g., dress up days, volunteer requests, signing forms, field trips) for their two children.
    Each action item should generally be about one child, however there may be some exceptions, in which case you can write "both". Set child_name to the name of that child.

    Also create a general_summary containing only the most relevant non-actionable school or childcare announcements. Write it as 2-5 concise bullets, with one announcement per line and each line starting with "- ". Prioritize closures, schedule changes, major dates, safety or policy updates, and information that affects the family. Omit marketing, routine newsletters, duplicate action items, and low-value details. If there are no relevant announcements, return an empty string.
    
    Pay special attention to emails and events concerning these specific institutions:
    - School: {school_name} is {child_name_1}'s school.
    - Childcare Center: {childcare_name} is {child_name_2}'s childcare center.
    
    Ignore standard newsletters, marketing, or general updates that don't contain deadline-driven requirements. 
    Disregard events that occurred in the past relative to today.

    For each action item, also extract the original sender and the date the email was received. 
    Format the email date into a clean, readable format (e.g., 'Oct 24'). Combine action items if they are about the same event and have the same deadline. For example class sign up newsletters will list multiple classes, but you can combine them into one action item with a summary like "Sign up for classes: Biking 101, Biking 102, and Intro to Jumps" and the same deadline.

    Ignore emails that are not meant for {grade} grade parents or {childcare_level} unless it is from the school or childcare center.
    
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
                "description": "Two to five concise bullets about the most relevant non-actionable school or childcare announcements. Each bullet starts with '- '. Return an empty string when there are no relevant announcements."
            },
            "action_items": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "event_date": {"type": "STRING", "description": "Date of the event or deadline."},
                        "child_name": {"type": "STRING", "description": "The name of exactly one child this action item pertains to."},
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

def analyze_parentsquare_emails(emails: list[dict]) -> SchoolDigest:
    """Sends ParentSquare emails to Gemini with strict teacher filtering."""
    client = genai.Client(vertexai=True, project=os.environ.get("GCP_PROJECT_ID"), location="us-central1")
    
    name = os.environ.get("CHILD_NAME_1", "Child 1")
    grade = os.environ.get("KIDS_GRADE", "their grade")
    teacher_name = os.environ.get("TEACHER_NAME", "their teacher")
    email_text_block = json.dumps(emails, indent=2)
    
    prompt = f"""
    You are an executive assistant managing ParentSquare communications for {grade} grade families.
    Review the following ParentSquare emails. 
    
    YOUR GOAL: Extract critical updates, action items, and messages sent directly by or pertaining to their teacher/director: {teacher_name}.
    The tracked child is {name}; set child_name to that child's name.
    
    STRICT EXCLUSIONS: 
    - When items are not actionable: Summarize very succinctly in bullets general school-wide blasts, district announcements, and generic PTSA newsletters in one message.
    - Be more descriptive when the teacher is the sender or the message is directly relevant to the child. 
    - Disregard events that occurred in the past relative to today.
    
    For each action item, also extract the original sender and the date the email was received. 
    Format the email date into a clean, readable format (e.g., 'Oct 24').
    Each action item must be about exactly one child. Set child_name to the name of that child.
    
    Here are the emails:
    {email_text_block}
    """
    
    # Use the same unrolled schema defined in your other function
    unrolled_schema = {
        "type": "OBJECT",
        "properties": {
            "has_action_items": {"type": "BOOLEAN"},
            "general_summary": {
                "type": "STRING",
                "description": "Two to five concise bullets about the most relevant non-actionable school or childcare announcements. Each bullet starts with '- '. Return an empty string when there are no relevant announcements."
            },
            "action_items": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "event_date": {"type": "STRING", "description": "Date of the event or deadline."},
                        "child_name": {"type": "STRING", "description": "The name of exactly one child this action item pertains to."},
                        "summary": {"type": "STRING", "description": "A brief description of the event."},
                        "required_action": {"type": "STRING", "description": "Exactly what the parent needs to do."},
                        "source_sender": {"type": "STRING", "description": "Who sent the original email."}, 
                        "email_date": {"type": "STRING", "description": "When the email was received."}   
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
    
    return SchoolDigest.model_validate_json(response.text)