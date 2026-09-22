# kid-bot
Never miss crazy hair day again. 

### Deployment Status

[![Deploy School Agent](https://github.com/Sunny-Dee/kid-bot/actions/workflows/deploy.yaml/badge.svg)](https://github.com/Sunny-Dee/kid-bot/actions/workflows/deploy.yaml)

# Github Copespace Setup

To setup your environment in a Github codespace run the following 

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

# Dev Environment Setup

Authenticate into GCP 

```shell
gcloud auth login
gcloud auth application-default login
gcloud config set project kid-bot-501018
```

# Generate Gmail Token

__Note:__ If you are in a GitHub Codespace run make sure you first run the setup commands above. 

1. Download your GCP OAuth client credentials from GCP Console (APIs & Services > Credentials > OAuth 2.0 Client IDs > `<your client>` > Add a secret > Download JSON) 

1. Save the file as `client_secret.json` in the root directory. 

1. Then run:
 
```shell
pip install google-auth-oauthlib
python generate_token.py
```
1. The command will send you to an authentication page, accept permissions (likely will require you to say you trust this app), the generate a localhost URL on port 8080. Copy the URL and fill out the following command in a __new terminal window__:

```shell
curl "http://localhost:8080/?state=YOUR_STATE&code=YOUR_CODE&scope=YOUR_SCOPE"
```

Where the values are present as URL query params. You should see `AUTHENTICATION SUCCESSFUL!` and the token printed on the first terminal window. 
