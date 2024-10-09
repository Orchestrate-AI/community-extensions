import os
import sys
import json
import redis
from crewai import Agent, Task, Crew, Process, LLM
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from crewai_tools import SerperDevTool, GithubSearchTool
from git import Repo
from github import Github, GithubException, Auth, GithubIntegration
import logging

# Set up logging to output to stdout
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load environment variables
WORKFLOW_INSTANCE_ID = os.getenv('WORKFLOW_INSTANCE_ID')
WORKFLOW_EXTENSION_ID = os.getenv('WORKFLOW_EXTENSION_ID')
REDIS_HOST_URL = os.getenv('REDIS_HOST_URL')
REDIS_USERNAME = os.getenv('REDIS_USERNAME')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_CHANNEL_IN = os.getenv('REDIS_CHANNEL_IN')
REDIS_CHANNEL_OUT = os.getenv('REDIS_CHANNEL_OUT')
REDIS_CHANNEL_READY = os.getenv('REDIS_CHANNEL_READY')

# Validate required environment variables
required_env_vars = [
    'WORKFLOW_INSTANCE_ID', 'WORKFLOW_EXTENSION_ID', 'REDIS_HOST_URL',
    'REDIS_USERNAME', 'REDIS_PASSWORD', 'REDIS_CHANNEL_IN',
    'REDIS_CHANNEL_OUT', 'REDIS_CHANNEL_READY'
]

missing_env_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_env_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_env_vars)}")

# Initialize Redis clients
publisher = redis.Redis(host=REDIS_HOST_URL, username=REDIS_USERNAME, password=REDIS_PASSWORD)
subscriber = redis.Redis(host=REDIS_HOST_URL, username=REDIS_USERNAME, password=REDIS_PASSWORD)

def clone_repo_and_set_guideline():
    # Clone the community-extensions repository
    repo_url = "https://github.com/Orchestrate-AI/community-extensions.git"
    repo_path = "./community-extensions"
    if not os.path.exists(repo_path):
        Repo.clone_from(repo_url, repo_path)
    else:
        repo = Repo(repo_path)
        repo.remotes.origin.pull()

    # Read context files
    def read_file(filename):
        with open(os.path.join(repo_path, filename), 'r') as file:
            return file.read()

    readme_content = read_file('README.md')
    guide_content = read_file('guide-js.md')
    communication_content = read_file('extension-communication.md')

    return f"""
    Extension Creation Guideline:
    
    README.md:
    {readme_content}

    guide-js.md:
    {guide_content}

    extension-communication.md:
    {communication_content}
    """

def create_extension(extension_spec, github_app_id, github_private_key, api_keys, model_config, guideline):
    # Initialize LLMs
    claude = ChatAnthropic(anthropic_api_key=api_keys['anthropic'], model="claude-3-5-sonnet-20240620")
    gpt4 = ChatOpenAI(api_key=api_keys['openai'], model_name="gpt-4", temperature=0.7)

    llm = LLM(
        model="claude-3-5-sonnet-20240620",
        temperature=0.7,
        # base_url="https://api.openai.com/v1",
        api_key=api_keys['anthropic']
    )
    

    # Create tools
    search_tool = SerperDevTool(api_key=api_keys['serper'])
    # github_tool = GithubSearchTool(gh_token=github_token, content_types=['code'])

    library_checker = Agent(
        role='Library Version Checker',
        goal='Ensure the latest versions of libraries are used',
        backstory='You are an expert in software dependencies and library versioning. Your job is to verify and update library versions to the most recent stable releases.',
        verbose=True,
        allow_delegation=False,
        llm=llm,
        tools=[search_tool]
    )

    developer = Agent(
        role='Developer',
        goal='Create extension code and structure',
        backstory='You are a skilled programmer with expertise in creating modular, efficient code. You will use the most recent LTS version of any language or framework that is most suitable for the extension.',
        verbose=True,
        allow_delegation=True,
        llm=llm
    )

    validator = Agent(
        role='Validator',
        goal='Ensure the extension follows all guidelines and requirements',
        backstory='You are a meticulous reviewer with a keen eye for detail. Your job is to validate that all guidelines and requirements have been followed in the extension creation.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    development_task = Task(
        description=f"""Use this guideline: 
        {guideline}

        Any data needed by the extension is passed through inputs. No additional environment variables must be added.

        Extension Specification:
        {extension_spec}
        Use whatever language that is best for the extension. Don't limit yourself to the language specified in the guideline.

        Do not include any additional environment variables other than the ones specified in the guideline.

        Provide your output in a structured format using the following tags for each file:
        <<<EXTENSION_NAME_START>>>
        Name of the extension based on service and action ex: Slack-SendNotification, Gmail-SendEmail, etc.
        <<<EXTENSION_NAME_END>>>

        <<<EXTENSION_DESCRIPTION_START>>>
        Description of the extension
        <<<EXTENSION_DESCRIPTION_END>>>

        <<<FILE_START>>>filename.extension
        [Your code here]
        <<<FILE_END>>>""",
        expected_output="The complete code implementation of the extension, with each file formatted with the specified tags. Do not include any additional text or comments outside the tags.",
        agent=developer
    )

    validation_task = Task(
        description=f"""Review the extension created by the Developer and ensure it follows all guidelines and requirements:

        Guidelines:
        {guideline}

        Extension Specification:
        {extension_spec}

        Verify the following:
        1. The extension uses the correct language and framework as specified in the guidelines.
        2. All required files are present (e.g., manifest.json, README.md, main script).
        3. The manifest.json file contains all necessary fields and follows the correct format.
        4. The README.md file includes all required sections (Description, Installation, Usage, etc.).
        5. The main script follows the communication protocol outlined in the guidelines.
        6. The code follows best practices and is efficient.
        7. Any data needed by the extension is passed through inputs. No additional environment variables must be added.

        If any issues are found, provide specific feedback on what needs to be corrected. If everything is correct, confirm that the extension meets all requirements.

        Your output should be in the following format:
        <<<VALIDATION_RESULT>>>
        [Your detailed review and feedback here]
        <<<VALIDATION_RESULT_END>>>
        """,
        expected_output="A detailed review of the extension, highlighting any issues found or confirming that all requirements are met.",
        agent=validator
    )

    library_check_task = Task(
        description=f"""Review the code created by the Developer and ensure all imported libraries are using their most recent stable versions. Use the SerperDevTool to search for the latest versions. If any libraries are outdated, provide the updated import statements or installation commands.

        Your output should be in the following format:
        <<<LIBRARY_CHECK>>>
        [Your detailed review and update suggestions here]
        <<<LIBRARY_CHECK_END>>>
        """,
        expected_output="A detailed review of the libraries used, with suggestions for updates if needed.",
        agent=library_checker
    )

    # Create the crew
    extension_crew = Crew(
        agents=[developer, validator, library_checker],
        tasks=[development_task, validation_task, library_check_task],
        verbose=True,
        process=Process.sequential,
        manager_llm=llm,
        full_output=True
    )

    # Execute tasks
    result = extension_crew.kickoff()

    # print('Result: ', result)

    # Extract extension name and description
    extension_name = result.tasks_output[0].raw.split('<<<EXTENSION_NAME_START>>>')[1].split('<<<EXTENSION_NAME_END>>>')[0].strip()
    extension_description = result.tasks_output[0].raw.split('<<<EXTENSION_DESCRIPTION_START>>>')[1].split('<<<EXTENSION_DESCRIPTION_END>>>')[0].strip()
    # Parse the result to extract different files
    files_to_create = parse_result(result)

    # Create a new branch and commit changes
    
    new_branch, pr_url = create_branch_and_commit(extension_name, files_to_create, github_app_id, github_private_key)

    # Print created files
    print("Created files:")
    for file_name in files_to_create.keys():
        print(f"- {file_name}")

    return f"Extension '{extension_name}' created. New branch: '{new_branch}'. Pull request created: {pr_url}"

def parse_result(crew_output):
    files = {}
    current_file = None
    current_content = []

    for task_output in crew_output.tasks_output:
        print('task_output: ', task_output)
        lines = task_output.raw.split('\n')
        for line in lines:
            if line.startswith("<<<FILE_START>>>"):
                if current_file:
                    files[current_file] = '\n'.join(current_content)
                current_file = line.split("<<<FILE_START>>>")[1].strip()
                current_content = []
            elif line.startswith("<<<FILE_END>>>"):
                if current_file:
                    files[current_file] = '\n'.join(current_content)
                    current_file = None
                    current_content = []
            elif current_file:
                current_content.append(line)

    return files

def create_branch_and_commit(extension_name, files_to_create, github_app_id, github_private_key):
    try:
        # Authenticate as GitHub App
        print(f"Attempting to authenticate with GitHub App ID: {github_app_id}")
        auth = Auth.AppAuth(github_app_id, github_private_key)
        gi = GithubIntegration(auth=auth)
        
        # Get the app installation
        app = gi.get_app()
        repo_name = "Orchestrate-AI/community-extensions"
        installations = gi.get_installations()
        installation = next((i for i in installations if repo_name in [r.full_name for r in gi.get_app_installation(i.id).get_repos()]), None)
        
        if not installation:
            raise ValueError(f"No installation found for repository: {repo_name}")
        
        # Get an authenticated Github instance for this installation
        access_token = gi.get_access_token(installation.id).token
        g = Github(access_token)

        # Get the repository
        repo = g.get_repo(repo_name)

        # Create a new branch for the extension
        main_branch = repo.get_branch("main")
        new_branch = f"new-extension-{extension_name}"
        repo.create_git_ref(f"refs/heads/{new_branch}", main_branch.commit.sha)

        # Create files in the new branch
        for file_name, file_content in files_to_create.items():
            file_path = f"{extension_name}/{file_name}"
            repo.create_file(
                path=file_path,
                message=f"Add {file_name} for {extension_name}",
                content=file_content,
                branch=new_branch
            )

        # Create a pull request
        pr = repo.create_pull(
            title=f"Add new extension: {extension_name}",
            body=f"This PR adds a new extension: {extension_name}",
            head=new_branch,
            base="main"
        )

        return new_branch, pr.html_url

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

def process_message(message, guideline):
    try:
        data = json.loads(message)
        extension_spec = data['inputs']['extension_spec']
        github_app_id = data['inputs']['github_app_id']
        github_private_key = data['inputs']['github_private_key']
        api_keys = {
            'openai': data['inputs']['openai_api_key'],
            'anthropic': data['inputs']['anthropic_api_key'],
            'serper': data['inputs']['serper_api_key']
        }
        model_config = {
            'ideator': data['inputs'].get('ideator_model', 'claude-2'),
            'developer': data['inputs'].get('developer_model', 'gpt-4'),
            'documenter': data['inputs'].get('documenter_model', 'gpt-4'),
            'reviewer': data['inputs'].get('reviewer_model', 'claude-2')
        }
        
        result = create_extension(extension_spec, github_app_id, github_private_key, api_keys, model_config, guideline)
        
        return {
            'status': 'success',
            'result': result
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def run_extension(input_data):
    try:
        guideline = clone_repo_and_set_guideline()
        
        extension_spec = input_data['inputs']['extension_spec']
        github_app_id = input_data['inputs']['github_app_id']
        github_private_key = input_data['inputs']['github_private_key']
        api_keys = {
            'openai': input_data['inputs']['openai_api_key'],
            'anthropic': input_data['inputs']['anthropic_api_key'],
            'serper': input_data['inputs']['serper_api_key']
        }
        model_config = {
            'ideator': input_data['inputs'].get('ideator_model', 'claude-2'),
            'developer': input_data['inputs'].get('developer_model', 'gpt-4'),
            'documenter': input_data['inputs'].get('documenter_model', 'gpt-4'),
            'reviewer': input_data['inputs'].get('reviewer_model', 'claude-2')
        }
        
        result = create_extension(extension_spec, github_app_id, github_private_key, api_keys, model_config, guideline)
        
        return {
            'status': 'success',
            'result': result
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def main():
    try:
        # Publish ready message
        publisher.publish(REDIS_CHANNEL_READY, '')
        
        # Clone repo and set guideline after sending ready message
        guideline = clone_repo_and_set_guideline()
        
        # Subscribe to input channel
        pubsub = subscriber.pubsub()
        pubsub.subscribe(REDIS_CHANNEL_IN)
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                result = process_message(message['data'], guideline)
                
                output = {
                    'type': 'completed' if result['status'] == 'success' else 'failed',
                    'workflowInstanceId': WORKFLOW_INSTANCE_ID,
                    'workflowExtensionId': WORKFLOW_EXTENSION_ID,
                    'output': result
                }
                
                publisher.publish(REDIS_CHANNEL_OUT, json.dumps(output))
                
                # Unsubscribe and exit after processing one message
                pubsub.unsubscribe(REDIS_CHANNEL_IN)
                break
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Clean up Redis connections
        publisher.close()
        subscriber.close()

if __name__ == "__main__":
    main()