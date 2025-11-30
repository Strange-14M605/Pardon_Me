import os
from dotenv import load_dotenv
from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.models import Gemini
from google.adk.tools import AgentTool
from .pipeline_agents import user_analyst, code_analyst, jargon_detector, readability_rewriter, aggregator

load_dotenv()
MODEL = Gemini(
    model="gemini-2.5-flash-lite",
    api_key=os.getenv("GOOGLE_API_KEY")
)

pipeline_agent = SequentialAgent(
    name="pipeline_agent",
    sub_agents=[
        user_analyst,
        code_analyst,
        jargon_detector,
        readability_rewriter,
        aggregator
    ],
)

# Define the root agent that uses the pipeline agent as a tool
root_agent = LlmAgent(
    name= "Pardon_Me",
    model=MODEL,
    instruction = """
    You are the Root Conversation Agent. Your role is to handle user queries related to the GitHub repository.
    Your only job is:
    ALWAYS call the `pipeline_agent` tool for every user request related to code, GitHub repositories, files, directories, or technical explanations.
    For ALL such queries, simply pass the entire user message to `pipeline_agent` exactly as the user wrote it.
    Always ensure that your responses are accurate, concise, and relevant to the user's needs.
    """,
    tools=[AgentTool(pipeline_agent)],
)

# AGENT = root_agent