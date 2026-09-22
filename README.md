# kid-bot
Never miss crazy hair day again. 

### Deployment Status

[![Deploy School Agent](https://github.com/Sunny-Dee/kid-bot/actions/workflows/deploy.yaml/badge.svg)](https://github.com/Sunny-Dee/kid-bot/actions/workflows/deploy.yaml)

# Github Copespace setup

To setup your environment in a Githun codespace run the following 

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