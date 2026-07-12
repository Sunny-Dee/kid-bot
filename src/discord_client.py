import os
import requests
from vertex_client import SchoolDigest

def send_to_discord(digest: SchoolDigest):
    """Formats the digest and posts it to a Discord webhook."""
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("No Discord webhook configured.")
        return

    # If there are no action items, we skip sending a daily alert to reduce noise.
    if not digest.has_action_items:
        print("No action items found today. Skipping Discord notification.")
        return

    embeds = []
    for item in digest.action_items:
        embeds.append({
            "title": f"⚠️ Action Required: {item.summary}",
            "color": 15158332, # Red color for visibility
            "fields": [
                {"name": "Date", "value": item.event_date, "inline": True},
                {"name": "Child", "value": item.child_name, "inline": True},
                {"name": "What you need to do", "value": item.required_action, "inline": False}
            ]
        })
        
    embeds.append({
        "title": "General Summary",
        "description": digest.general_summary,
        "color": 3447003 # Blue color for general info
    })

    payload = {
        "content": "🚨 **New School Action Items Detected!**",
        "embeds": embeds
    }

    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()