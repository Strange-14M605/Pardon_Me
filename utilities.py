# utilities.py
import os
from typing import List, Union
from google.adk.runners import Runner
from google.genai.types import Content, Part

USER_ID = "default_user"

# helper functions
async def get_or_create_session(runner: Runner, session_id: str):
    """
    Try to fetch existing session; create if missing.
    Works across ADK versions that return None for missing sessions.
    """
    svc = runner.session_service
    app_name = runner.app_name

    session = await svc.get_session(app_name=app_name, user_id=USER_ID, session_id=session_id)
    if session:
        return session

    return await svc.create_session(app_name=app_name, user_id=USER_ID, session_id=session_id)


def extract_session_id_value(session_obj) -> str:
    """
    ADK changed session object fields between versions.
    Try common attributes to find the valid session ID.
    """
    for attr in ("session_id", "id", "session", "session_key"):
        if hasattr(session_obj, attr):
            return getattr(session_obj, attr)

    if isinstance(session_obj, dict):
        for key in ("session_id", "id", "session", "session_key"):
            if key in session_obj:
                return session_obj[key]

    raise RuntimeError(f"Cannot extract session id from: {session_obj!r}")


# main call - for streaming
async def run_session(
    runner: Runner,
    user_queries: Union[str, List[str]],
    session_name: str
):
    """
    Takes one or many user messages and streams responses from ADK.
    Preserves session context.
    Returns final aggregated output.
    """
    if isinstance(user_queries, str):
        queries = [user_queries]
    else:
        queries = list(user_queries)

    # get/create persistent session
    session = await get_or_create_session(runner, session_name)
    sid = extract_session_id_value(session)

    all_turns_output = []

    for query in queries:
        content = Content(role="user", parts=[Part(text=str(query))])

        fragments = []

        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=sid,
            new_message=content
        ):
            if event.content and event.content.parts:
                text = event.content.parts[0].text
                if text and text.strip() != "None":
                    fragments.append(text)

        turn_output = "".join(fragments).strip()

        if turn_output:
            all_turns_output.append(turn_output)

    return "\n\n".join(all_turns_output)
