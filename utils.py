# utilities.py
from google.adk.runners import Runner
from google.genai.types import Content, Part

USER_ID = "default_user"

async def run_session(
    runner: Runner,
    query: str,
    session_name: str
):
    """
    Takes the user message and sends it to the runner.
    Preserves session context.
    Returns final aggregated output.
    """
    print(f"\n ### Session: {session_name}")
    session_service = runner.session_service
    app_name = runner.app_name
    
    # get/create persistent session
    try:
        session = await session_service.create_session(
            app_name=app_name, user_id=USER_ID, session_id=session_name
        )
    except:
        session = await session_service.get_session(
            app_name=app_name, user_id=USER_ID, session_id=session_name
        )    

    print(f"\nUser > {query}")
    
    # Convert the query string to the ADK Content format
    query = Content(role="user", parts=[Part(text=str(query))])
    
    all_turns_output = []
    fragments = []

    # Stream the agent's response asynchronously
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=query
    ):
        if event.content and event.content.parts:
            text = event.content.parts[0].text
            if text and text.strip() != "None":
                print(f"Pardon Me > ", text)
                fragments.append(text)

    turn_output = "".join(fragments).strip()

    if turn_output:
        all_turns_output.append(turn_output)

    return "\n\n".join(all_turns_output)
