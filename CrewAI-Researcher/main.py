# main.py
import os
from dotenv import load_dotenv
import redis
import json
from crewai import Agent, Task, Crew, Process
from langchain.chat_models import ChatOpenAI, ChatAnthropic

load_dotenv()

WORKFLOW_INSTANCE_ID = os.getenv('WORKFLOW_INSTANCE_ID')
WORKFLOW_EXTENSION_ID = os.getenv('WORKFLOW_EXTENSION_ID')
REDIS_HOST_URL = os.getenv('REDIS_HOST_URL')
REDIS_USERNAME = os.getenv('REDIS_USERNAME')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_CHANNEL_IN = os.getenv('REDIS_CHANNEL_IN')
REDIS_CHANNEL_OUT = os.getenv('REDIS_CHANNEL_OUT')
REDIS_CHANNEL_READY = os.getenv('REDIS_CHANNEL_READY')

redis_client = redis.Redis(
    host=REDIS_HOST_URL,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    decode_responses=True
)

def get_llm(model, api_key):
    if model.startswith('gpt-'):
        return ChatOpenAI(model=model, openai_api_key=api_key)
    elif model.startswith('claude-'):
        return ChatAnthropic(model=model, anthropic_api_key=api_key)
    else:
        raise ValueError(f"Unsupported model: {model}")

def process_message(message):
    inputs = json.loads(message)['inputs']
    topic = inputs.get('topic')
    openai_api_key = inputs.get('openai_api_key')
    anthropic_api_key = inputs.get('anthropic_api_key')
    researcher_model = inputs.get('researcher_model', 'gpt-4')
    writer_model = inputs.get('writer_model', 'gpt-4')

    if not topic:
        raise ValueError("Research topic is required")

    if not openai_api_key and not anthropic_api_key:
        raise ValueError("Either OpenAI or Anthropic API key is required")

    researcher_llm = get_llm(researcher_model, openai_api_key if researcher_model.startswith('gpt-') else anthropic_api_key)
    writer_llm = get_llm(writer_model, openai_api_key if writer_model.startswith('gpt-') else anthropic_api_key)

    researcher = Agent(
        role="Researcher",
        goal="Conduct thorough research on the given topic",
        backstory="You are an expert researcher with a keen eye for detail and the ability to find reliable information quickly.",
        llm=researcher_llm,
    )

    writer = Agent(
        role="Writer",
        goal="Synthesize research findings into a comprehensive report",
        backstory="You are a skilled writer with the ability to organize information clearly and present it in an engaging manner.",
        llm=writer_llm,
    )

    research_task = Task(
        description=f"Research the topic: {topic}. Gather key information, important facts, and relevant data.",
        agent=researcher
    )

    writing_task = Task(
        description="Write a comprehensive research report based on the findings. Include an introduction, main points, and a conclusion.",
        agent=writer
    )

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        verbose=True,
        process=Process.sequential
    )

    result = crew.kickoff()

    return {
        "topic": topic,
        "research_report": result,
        "models_used": {
            "researcher": researcher_model,
            "writer": writer_model
        }
    }

def main():
    redis_client.publish(REDIS_CHANNEL_READY, '')

    pubsub = redis_client.pubsub()
    pubsub.subscribe(REDIS_CHANNEL_IN)

    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                result = process_message(message['data'])
                output = {
                    "type": "completed",
                    "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                    "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                    "output": result
                }
                redis_client.publish(REDIS_CHANNEL_OUT, json.dumps(output))
            except Exception as e:
                error_output = {
                    "type": "failed",
                    "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                    "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                    "error": str(e)
                }
                redis_client.publish(REDIS_CHANNEL_OUT, json.dumps(error_output))
            finally:
                pubsub.unsubscribe(REDIS_CHANNEL_IN)
                break

if __name__ == "__main__":
    main()