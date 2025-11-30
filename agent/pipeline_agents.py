from google.adk.agents import LlmAgent
from google.adk.models import Gemini 
from .github_mcp_tool import github_mcp_tool

MODEL = Gemini(model="gemini-2.5-flash-lite")

user_analyst = LlmAgent(    
    name="user_analyst",
    model=MODEL,
    description="Understands what the user is actually asking for.",
    instruction="""
        Interpret the user’s request thoroughly.
        Extract their true intent, target files or components, expected output format,
        and any preferences in tone or detail. Provide a concise structured summary
        that captures exactly what the user wants the system to analyze or explain.""",
    output_key="user_intent",
)

code_analyst = LlmAgent(
    name="code_analyst",
    model=MODEL,
    description="Explains code using GitHub MCP and the user's clarified intent.",
    instruction="""
        Using the GitHub MCP toolset and the details in {user_intent}, locate and analyze
        the relevant code. Explain the code’s purpose, behavior, internal logic,
        dependencies, and execution flow. Present the explanation in accurate but
        approachable human language suited for general technical readers.""",
    tools=[github_mcp_tool],
    output_key="code_analysis",
)

jargon_detector = LlmAgent(
    name="jargon_detector",
    model=MODEL,
    description="Finds confusing terminology inside the technical analysis.",
    instruction="""
        Review the content in {code_analysis}. Identify any jargon, advanced terminology,
        framework-specific language, or acronyms that could confuse non-technical readers.
        List each identified term clearly and objectively without rewriting the analysis.""",
    output_key="jargon_list",
)

readability_rewriter = LlmAgent(
    name="readability_rewriter",
    model=MODEL,
    description="Converts complex technical explanations into beginner-friendly language.",
    instruction="""
        Rewrite {code_analysis} into a clean, readable explanation suitable for people
        with little or no technical background. Simplify complex ideas, define or remove
        terms found in {jargon_list}, and ensure the final version remains correct while
        maximizing clarity, flow, and accessibility.""",
    output_key="readable_code_analysis",
)

aggregator = LlmAgent(
    name="aggregator",
    model=MODEL,
    description="Creates the final merged explanation tailored to the user’s intent.",
    instruction="""
    Combine the depth of {code_analysis} with the clarity of {readable_code_analysis}.
    Produce a polished final report aligned fully with the goals expressed in
    {user_intent}. Structure the output cleanly, provide both technical and simplified
    perspectives, and ensure the final answer feels cohesive and user-focused. """,
    output_key="final_report",
)
