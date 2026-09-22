import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    client_secrets_file = 'client_secret.json'
    
    # You must download your OAuth Client ID JSON file from the Google Cloud Console,
    # rename it to 'client_secret.json', and place it in the same directory as this script.
    if not os.path.exists(client_secrets_file):
        print(f"Error: '{client_secrets_file}' not found.")
        print("Please download it from Google Cloud Console > APIs & Services > Credentials.")
        return

    print("Starting local web server for authentication...")
    
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, 
        SCOPES
    )
    
    # access_type='offline' instructs Google to return a refresh token
    # prompt='consent' forces the consent screen so a new refresh token is always generated
    # open_browser=False ensures it prints the URL cleanly for your Codespace workflow
    credentials = flow.run_local_server(
        port=8080, 
        access_type='offline', 
        prompt='consent',
        open_browser=False
    )
    
    print("\n" + "="*50)
    print("AUTHENTICATION SUCCESSFUL!")
    print("="*50)
    print(f"GMAIL_REFRESH_TOKEN:\n{credentials.refresh_token}")
    print("="*50)

if __name__ == '__main__':
    main()