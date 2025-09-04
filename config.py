import os
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient
# from azure.mgmt.automation import AutomationClient
from openai import AzureOpenAI

load_dotenv()

# Credentials and Identifiers
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
TENANT_ID = os.getenv('AZURE_TENANT_ID')
SUBSCRIPTION_ID = os.getenv('AZURE_SUBSCRIPTION_ID')
RESOURCE_GROUP = os.getenv('AZURE_RESOURCE_GROUP')
PROJECT_NAME = os.getenv('AZURE_PROJECT_NAME')
PROJECT_ENDPOINT = os.getenv('PROJECT_ENDPOINT')
CLASSIFICATION_AGENT_ID = os.getenv('CLASSIFICATION_AGENT_ID')
TROUBLESHOOTING_AGENT_ID = os.getenv('TROUBLESHOOTING_AGENT_ID')
TICKETING_AGENT_ID = os.getenv('TICKETING_AGENT_ID')

#  Azure OpenAI Configuration
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEPLOYMENT_NAME = "gpt-4o-mini"

# Automation Account Configuration
# AUTOMATION_ACCOUNT = os.getenv('AUTOMATION_ACCOUNT')
# HYBRID_WORKER_GROUP = os.getenv('HYBRID_WORKER_GROUP')
# RUNBOOK_NAME = os.getenv('RUNBOOK_NAME')

#  Client Initializations 

# Azure credential
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

# Azure OpenAI client (for LLM calls)
openai_client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=AZURE_ENDPOINT,
    api_key=OPENAI_API_KEY
)

# Azure AI Project client (for agent orchestration)
project_client = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential
)

# Azure Automation client
# automation_client = AutomationClient(credential, SUBSCRIPTION_ID)

print("Configuration and clients initialized successfully.")