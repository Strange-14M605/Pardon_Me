# Pardon_Me
A GitHub Repo Insight Agent

## Problem
Large GitHub repositories often read like dense technical forests—layers of code, scattered documentation, and enough jargon to overwhelm even experienced developers. The result is slow onboarding, unnecessary confusion, and a constant sense of “Where do I even start?”

I can see it affecting various types of people including:
- **New contributors** struggling to understand project structure
- **Technical writers** needing to document unfamiliar systems
- **Product managers** seeking to grasp implementation details
- **Educators** looking to explain real-world code to students
  
The bottleneck isn't just about missing documentation—it's about the gap between how code is written and how humans naturally understand systems.

## Solution
This project grew out of that gap—a desire to make repositories a little less intimidating and a lot more readable.

Pardon_Me is a focused multi-agent system that understands user intent, analyzes the repo via GitHub MCP, identifies jargon, and produces a clear, accessible interpretation, while still allowing users to engage with it conversationally. They can ask follow-up questions, clarify unclear sections, or dive deeper into specific components—much like consulting a well-informed teammate who already understands the entire repository.


## Project Journey and Evolution

Pardon_Me started off as a an idea that involved Parallel execution where each sub agent would analyse the code from different stakeholder POVs like a designer, product manager, QA engineer, etc. And then provide the user with an aggregated insight. The idea seemed solid but I had to pivot pretty quickly due to Github constraints and timeouts when I called the MCP for each sub-agent simultaneously. One workaround was to align the agents sequentially, but that defeated the entire purpose of parallel execution. 

Additionally, I tried using them as an 'AgentTeam', where a parent LlmAgent would dynamically decide which sub-agents to execute parallelly- but google adk seems to not have that feature yet (I could be wrong, please let me know if you know a way).

Finally, I settled on a SequentialAgent solution where we could dedicate each agent for sequential tasks like Analyse user query-> extract essential code features -> decompose technical jargon -> summarise for easy understanding. That said, I did come across a couple hurdles while building this solution as well like:
1. Configuring the GitHub remote server
2. AgentTool's output isn't a valid adk event so when I tried to retrieve it for context compaction, it returned format errors. (I wasn't able to fix this - [an open issue](https://github.com/google/adk-python/issues/3633) )


## Agent Architecture/Pipeline

<img width="1062" height="791" alt="image" src="https://github.com/user-attachments/assets/e1f49a37-dee6-4564-a067-46989449021a" />


Once the user inputs a query, the backend system triggers the root_agent, which then uses five specialized agents in sequence:

1. **User Analyst** 
   - Interprets user requests and extracts true intent
   - Identifies target files, components, and expected output format

2. **Code Analyst** 
   - Retrieves and analyzes code using GitHub MCP toolset
   - Explains purpose, behavior, logic, dependencies, and execution flow
> The GitHub MCP toolset provides secure, read-only access to repositories:
>
> ```python
> github_mcp_tool = McpToolset(
>     connection_params=StreamableHTTPServerParams(
>         url="https://api.githubcopilot.com/mcp/",
>         headers={
>             "Authorization": f"Bearer {GITHUB_TOKEN}",
>             "X-MCP-Toolsets": "all",
>             "X-MCP-Readonly": "true"
>         },
>         timeout=30,
>     ),
> )
> ```
>
> This enables the Code Analyst agent to fetch live repository data without manual file uploads.


3. **Jargon Detector**
   - Scans technical analysis for confusing terminology
   - Identifies framework-specific language, acronyms, and advanced concepts

4. **Readability Rewriter** 
   - Transforms technical explanations into beginner-friendly language while maintaining correctness
   - Removes or defines jargon identified in previous step

5. **Aggregator** 📋
   - Merges technical depth with accessibility
   - Produces final polished report aligned with user intent

Each of these agents have an output_key which is propagated to the next agent accordingly:
```python
# Each agent outputs to a specific key
user_analyst → output_key="user_intent"
code_analyst → output_key="code_analysis"
jargon_detector → output_key="jargon_list"
readability_rewriter → output_key="readable_code_analysis"
aggregator → output_key="final_report"
```
### NOTE: Session Persistence

Conversations are stored in SQLite, allowing users to:
- Continue previous conversations
- Reference earlier explanations
- Build understanding incrementally
```python
session_service = DatabaseSessionService(db_url="sqlite+aiosqlite:///data/sessions.db")
```
### Summary of Features

- **Multi-layered Analysis/ Multi-Agent system**: Combines technical depth with beginner-friendly explanations with the help of Sequential Agents
- **Conversational Understanding**: Users can ask follow-up questions, clarify unclear sections, or dive deeper into specific components—much like consulting a well-informed teammate who already understands the entire repository
- **Session Persistence**: Conversations are stored in SQLite, enabling follow-up questions and context retention
- **Direct GitHub Integration**: Uses GitHub MCP to access live repository data
- **Streaming Responses**: Real-time agent output processing
- **Modular Design**: Each agent has a single, well-defined responsibility
  
## High Level Overview & Project Structure

<img width="1407" height="772" alt="image" src="https://github.com/user-attachments/assets/a8f2f65a-33b2-4b4d-8d84-55be880aa76f" />


- **Framework**: FastAPI for REST API backend
- **AI Engine**: Google Gemini 2.5 Flash Lite via ADK
- **GitHub Integration**: GitHub MCP (Model Context Protocol) for repository access
- **Session Management**: SQLite database for persistent conversations
- **Frontend**: Vanilla HTML/CSS/JavaScript (served statically)

### Project Structure
```
pardon_me/
├── agent/
│   ├── github_mcp_tool.py      # GitHub MCP toolset configuration
│   ├── pipeline_agents.py       # Five specialized agents
│   └── root_agent.py            # Root agent and pipeline wrapper
├── data/
│   └── sessions.db              # SQLite session storage (auto-created)
├── static/
│   ├── index.html               # Frontend UI
│   ├── script.js                # Client-side logic
│   └── style.css                # Styling
├── .env                         # Environment variables (create this)
├── .gitignore                   # Git ignore rules
├── app.py                       # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── utils.py                     # Session management utilities
```

## Instructions for Setup

### Prerequisites

- Python 3.8 or higher
- GitHub Personal Access Token (PAT) with repository read access
- Google Gemini API Key

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/pardon_me.git
cd pardon_me
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages include:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `python-dotenv` - Environment variable management
- `google-adk` - Google Agent Development Kit
- `google-genai` - Google Generative AI SDK
- `pydantic` - Data validation
- `aiosqlite` - Async SQLite support

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:
```bash
touch .env
```

Add your API credentials:
```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
GITHUB_MCP_PAT=your_github_personal_access_token_here
```

### Step 4: Run the Application
```bash
uvicorn app:app --reload
```

### Step 5: Access the UI

Open your browser and navigate to:
```
http://localhost:8000
```

You'll see the Pardon_Me chat interface where you can start asking questions about GitHub repositories.

<img width="1918" height="1047" alt="image" src="https://github.com/user-attachments/assets/5b94f6be-a952-46d6-b356-83e6980c83a6" />


### Example Queries

Try asking:
- "Explain the main authentication flow in [repo-owner/repo-name]"
- "What does the database schema look like in this project?"
- "How does the API routing work in app.py?"
- "Break down the agent pipeline in simple terms"

<img width="1918" height="1078" alt="image" src="https://github.com/user-attachments/assets/a1b3a356-5082-4b95-932a-ea4944c57c98" />

> You can see the logs by `LoggingPlugin()` (for obervability) show up on your terminal like this:

> <img width="1426" height="682" alt="image" src="https://github.com/user-attachments/assets/23ef38e5-f7c4-464a-ae28-88d04674aa5b" />


## Title and design 
I titled the project **Pardon_Me** after the numerous times I've had to ask someone to repeat themselves when they seem to talk in another language made up of technical jargon! I find myself muttering it to myself while scrambling through a Github Repo I just opened as well. 

As for the design, I just wanted something warm to work with while I practice. This was the initial prototype:

<img width="328" height="313" alt="image" src="https://github.com/user-attachments/assets/33db5098-9dae-476a-885b-030a3dd94c0b" />


## Future Enhancements

- **Enhanced UI**: Rich code syntax highlighting and interactive diagrams
- **Advanced Analysis**: Detect code smells, security issues, and architectural patterns
- **Advanced Features**: Allow user with non-tech backgrounds to edit code using simple commands
- **Deployment** (obviously🥹): Cloud deployment using Google Cloud Run or similar platform

## List of Resources
[Kaggle: 5-Day AI Agents Intensive Course with Google]([https://example.com](https://www.kaggle.com/learn-guide/5-day-agents))
[Google ADK Docs]([https://example.com](https://google.github.io/adk-docs/))
[Remote GitHub MCP Server](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)
[FastAPI]([https://example.com](https://fastapi.tiangolo.com/))
[Excalidraw]([https://example.com](https://excalidraw.com/)) (for diagrams)


**Built with ❤️ -Jo**
