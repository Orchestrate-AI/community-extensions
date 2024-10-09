import os
import json
from main import run_extension

# Set up environment variables
os.environ['WORKFLOW_INSTANCE_ID'] = 'test-instance'
os.environ['WORKFLOW_EXTENSION_ID'] = 'test-extension'
os.environ['REDIS_HOST_URL'] = 'dummy-host'
os.environ['REDIS_USERNAME'] = 'dummy-user'
os.environ['REDIS_PASSWORD'] = 'dummy-password'
os.environ['REDIS_CHANNEL_IN'] = 'dummy-in'
os.environ['REDIS_CHANNEL_OUT'] = 'dummy-out'
os.environ['REDIS_CHANNEL_READY'] = 'dummy-ready'

# Test input data
test_input = {
    'inputs': {
        'extension_spec': '<Salesforce,Creates a new lead in the CRM,Create Lead>',
        'github_app_id': os.getenv('GITHUB_APP_ID', 'your-github-app-id'),
        'github_private_key': os.getenv('GITHUB_PRIVATE_KEY', 'your-github-private-key'),
        'openai_api_key': os.getenv('OPENAI_API_KEY', 'your-openai-api-key'),
        'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY', 'your-anthropic-api-key'),
        'serper_api_key': os.getenv('SERPER_API_KEY', 'your-serper-api-key'),
        'ideator_model': 'claude',
        'developer_model': 'claude',
        'documenter_model': 'claude',
        'reviewer_model': 'claude'
    }
}

def run_e2e_test():
    print("Starting E2E test for Extension Generator...")
    
    result = run_extension(test_input)
    
    print("Test completed. Result:")
    print(json.dumps(result, indent=2))
    
    if result['status'] == 'success':
        print("E2E test passed successfully!")
        print("New branch:", result['result']['new_branch'])
        print("Pull request URL:", result['result']['pr_url'])
    else:
        print("E2E test failed.")
        print("Error message:", result['message'])

if __name__ == "__main__":
    run_e2e_test()