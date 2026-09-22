import os
import requests
from vertex_client import SchoolDigest

# UPDATE: Add webhook_url as a parameter
def send_to_discord(digest: SchoolDigest, webhook_url: str = None):
    """Formats the digest and posts it to a Discord webhook."""
    # Fallback to the default general webhook if none is provided
    if not webhook_url:
        webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        
    if not webhook_url:
        print("No Discord webhook configured.")
        return

    if not digest.has_action_items and not digest.general_summary.strip():
        print("No action items or general announcements found today. Skipping Discord notification.")
        return

    embeds = []
    for item in digest.action_items:
        embeds.append({
            "title": f"⚠️ Action Required: {item.summary}",
            "color": 15158332, 
            "fields": [
                {"name": "Date", "value": item.event_date, "inline": True},
                {"name": "Child", "value": item.child_name, "inline": True},
                {"name": "What you need to do", "value": item.required_action, "inline": False},
                {"name": "Source Email", "value": f"From: {item.source_sender}\nReceived: {item.email_date}", "inline": False}
            ]
        })
        
    if digest.general_summary.strip():
        embeds.append({
            "title": "General Announcements",
            "description": digest.general_summary,
            "color": 3447003
        })

    payload = {
        "content": "🚨 **New School Action Items Detected!**",
        "embeds": embeds
    }

    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()