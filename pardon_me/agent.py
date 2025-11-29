from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.models import Gemini
from google.adk.tools import AgentTool
from pardon_me.pipeline_agents import user_analyst, code_analyst, jargon_detector, readability_rewriter, aggregator

MODEL = Gemini(model="gemini-2.5-flash-lite")

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
    name= "Root_Conversation_Agent",
    model=MODEL,
    instruction = """
    You are the Root Conversation Agent. Your role is to handle user queries related to the GitHub repository.
    For simple queries, provide direct answers using the GitHub MCP toolset.
    For complex queries that require in-depth analysis or multiple perspectives, delegate the task to the Sequential_Specialist_Agent.
    Always ensure that your responses are accurate, concise, and relevant to the user's needs.
    """,
    tools=[AgentTool(pipeline_agent)],
)

AGENT = root_agent