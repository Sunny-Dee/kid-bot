import os
import sys
import time
from gmail_client import fetch_recent_school_emails
from vertex_client import analyze_emails
from discord_client import send_to_discord
from db_client import get_last_run_timestamp, update_last_run_timestamp

def main():
    print("Starting School Communication Agent...")
    
    # Record the exact time this job started. We use this to update the DB later.
    current_run_time = int(time.time())
    
    required_vars = [
        "GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "GMAIL_REFRESH_TOKEN", 
        "GCP_PROJECT_ID", "DISCORD_WEBHOOK_URL"
    ]
    for var in required_vars:
        if not os.environ.get(var):
            print(f"Error: Missing required environment variable {var}")
            sys.exit(1)

    try:
        # 1. Get the high-water mark
        last_run_timestamp = get_last_run_timestamp()
        
        # 2. Fetch emails AFTER that mark
        print("Fetching recent emails...")
        emails = fetch_recent_school_emails(after_timestamp=last_run_timestamp)
        
        if not emails:
            print("No new emails found since the last run.")
            # Still update the timestamp so we don't look too far back next time!
            update_last_run_timestamp(current_run_time)
            return
            
        print(f"Found {len(emails)} new emails. Analyzing with Vertex AI...")
        digest = analyze_emails(emails)
        
        print("Analysis complete. Sending to Discord...")
        send_to_discord(digest)
        
        # 3. Only update the database if everything above succeeded
        update_last_run_timestamp(current_run_time)
        print("Job completed successfully.")
        
    except Exception as e:
        print(f"An error occurred during execution: {e}")
        # Notice we do NOT update the timestamp here. 
        # If it fails, tomorrow's run will try to process these emails again.
        sys.exit(1)

if __name__ == "__main__":
    main()