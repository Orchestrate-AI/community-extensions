import os
import logging
from dotenv import load_dotenv
import redis
import json
from crewai import Agent, Task, Crew, Process
from langchain_community.chat_models import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

WORKFLOW_INSTANCE_ID = os.getenv('WORKFLOW_INSTANCE_ID')
WORKFLOW_EXTENSION_ID = os.getenv('WORKFLOW_EXTENSION_ID')
REDIS_HOST_URL = os.getenv('REDIS_HOST_URL')
REDIS_USERNAME = os.getenv('REDIS_USERNAME')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
REDIS_CHANNEL_IN = os.getenv('REDIS_CHANNEL_IN')
REDIS_CHANNEL_OUT = os.getenv('REDIS_CHANNEL_OUT')
REDIS_CHANNEL_READY = os.getenv('REDIS_CHANNEL_READY')

redis_client = redis.Redis.from_url(
    url=REDIS_HOST_URL,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    decode_responses=True
)

def get_llm(model, api_key):
    logger.debug(f"Creating LLM instance for model: {model}")
    if model.startswith('gpt-'):
        return ChatOpenAI(model=model, openai_api_key=api_key)
    elif model.startswith('claude-'):
        return ChatAnthropic(model=model, anthropic_api_key=api_key)
    else:
        raise ValueError(f"Unsupported model: {model}")

def process_message(message):
    logger.info("Processing incoming message")
    inputs = json.loads(message)['inputs']
    topic = inputs.get('topic')
    openai_api_key = inputs.get('openai_api_key')
    anthropic_api_key = inputs.get('anthropic_api_key')
    researcher_model = inputs.get('researcher_model', 'gpt-4')
    writer_model = inputs.get('writer_model', 'gpt-4')

    logger.debug(f"Received topic: {topic}")
    logger.debug(f"Researcher model: {researcher_model}")
    logger.debug(f"Writer model: {writer_model}")

    if not topic:
        logger.error("Research topic is missing")
        raise ValueError("Research topic is required")

    if not openai_api_key and not anthropic_api_key:
        logger.error("API keys are missing")
        raise ValueError("Either OpenAI or Anthropic API key is required")

    researcher_llm = get_llm(researcher_model, openai_api_key if researcher_model.startswith('gpt-') else anthropic_api_key)
    writer_llm = get_llm(writer_model, openai_api_key if writer_model.startswith('gpt-') else anthropic_api_key)

    logger.debug("Creating Researcher agent")
    researcher = Agent(
        role="Researcher",
        goal="Conduct thorough research on the given topic",
        backstory="You are an expert researcher with a keen eye for detail and the ability to find reliable information quickly.",
        llm=researcher_llm,
    )
    logger.debug("Researcher agent created successfully")

    logger.debug("Creating Writer agent")
    writer = Agent(
        role="Writer",
        goal="Synthesize research findings into a comprehensive report",
        backstory="You are a skilled writer with the ability to organize information clearly and present it in an engaging manner.",
        llm=writer_llm,
    )
    logger.debug("Writer agent created successfully")

    logger.debug("Creating research task")
    research_task = Task(
        description=f"Research the topic: {topic}. Gather key information, important facts, and relevant data.",
        agent=researcher,
        expected_output="A comprehensive collection of research findings on the given topic."
    )
    logger.debug("Research task created successfully")
    logger.debug(f"Research task details: {research_task}")

    logger.debug("Creating writing task")
    writing_task = Task(
        description="Write a comprehensive research report based on the findings. Include an introduction, main points, and a conclusion.",
        agent=writer,
        expected_output="A well-structured research report synthesizing the gathered information."
    )
    logger.debug("Writing task created successfully")
    logger.debug(f"Writing task details: {writing_task}")

    logger.info("Creating Crew instance")
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        verbose=True,
        process=Process.sequential
    )
    logger.debug("Crew instance created successfully")

    logger.info("Starting Crew execution")
    result = crew.kickoff()
    logger.info("Crew execution completed")

    return {
        "topic": topic,
        "research_report": result,
        "models_used": {
            "researcher": researcher_model,
            "writer": writer_model
        }
    }

def main():
    logger.info("Starting main function")
    redis_client.publish(REDIS_CHANNEL_READY, '')
    logger.info(f"Published ready message to channel: {REDIS_CHANNEL_READY}")

    pubsub = redis_client.pubsub()
    pubsub.subscribe(REDIS_CHANNEL_IN)
    logger.info(f"Subscribed to input channel: {REDIS_CHANNEL_IN}")

    for message in pubsub.listen():
        if message['type'] == 'message':
            logger.info("Received message from Redis")
            try:
                result = process_message(message['data'])
                output = {
                    "type": "completed",
                    "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                    "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                    "output": result
                }
                redis_client.publish(REDIS_CHANNEL_OUT, json.dumps(output))
                logger.info(f"Published result to channel: {REDIS_CHANNEL_OUT}")
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}", exc_info=True)
                error_output = {
                    "type": "failed",
                    "workflowInstanceId": WORKFLOW_INSTANCE_ID,
                    "workflowExtensionId": WORKFLOW_EXTENSION_ID,
                    "error": str(e)
                }
                redis_client.publish(REDIS_CHANNEL_OUT, json.dumps(error_output))
                logger.info(f"Published error to channel: {REDIS_CHANNEL_OUT}")
            finally:
                pubsub.unsubscribe(REDIS_CHANNEL_IN)
                logger.info(f"Unsubscribed from channel: {REDIS_CHANNEL_IN}")
                break

if __name__ == "__main__":
    main()