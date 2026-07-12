import os
import sys
from gmail_client import fetch_recent_school_emails
from vertex_client import analyze_emails
from discord_client import send_to_discord

def main():
    print("Starting School Communication Agent...")
    
    # Ensure critical env vars are set before proceeding
    required_vars = [
        "GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "GMAIL_REFRESH_TOKEN", 
        "GCP_PROJECT_ID", "DISCORD_WEBHOOK_URL"
    ]
    for var in required_vars:
        if not os.environ.get(var):
            print(f"Error: Missing required environment variable {var}")
            sys.exit(1)

    try:
        print("Fetching recent emails...")
        emails = fetch_recent_school_emails(query="newer_than:1d")
        
        if not emails:
            print("No recent emails found in the specified timeframe.")
            return
            
        print(f"Found {len(emails)} emails. Analyzing with Vertex AI...")
        digest = analyze_emails(emails)
        
        print("Analysis complete. Sending to Discord...")
        send_to_discord(digest)
        
        print("Job completed successfully.")
        
    except Exception as e:
        print(f"An error occurred during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()