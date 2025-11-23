# services/assistant_service.py
import json
from ..services.ai_service import client, MODEL, _api_key_check

def generate_assistant_response(user_id, new_user_message):
    """
    Stateless assistant: does NOT persist user or assistant messages to the DB.
    Returns ({'assistant_response': text}, status_code)
    """
    error_check = _api_key_check()
    if error_check:
        return {'error': error_check}, 500

    # 1) System instruction and single-message context (stateless)
    system_instruction = (
        "You are the Smart Task Manager AI Assistant, powered by Gemini. "
        "Answer concisely, helpfully and professionally. If asked for task-specific advice, "
        "give actionable steps. You have access to the USER_ID but not the real name; if asked, "
        "tell the user that you only know their USER_ID and display it when requested."
    )

    # Build a single-string prompt that is simple and robust (same style used in working subtask code)
    prompt_text = (
        f"SYSTEM INSTRUCTION: {system_instruction}\n\n"
        f"USER_ID: {user_id}\n\n"
        f"User: {new_user_message}\n\n"
        "Assistant:"
    )

    # 2) Call Gemini with a single contents string
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt_text,
        )

        # response.text is used in other service files; keep same usage
        assistant_response = response.text.strip() if hasattr(response, 'text') else str(response)

        # Optional debug line (server logs)
        print(f"[Assistant - Stateless] user_id={user_id} assistant_preview={assistant_response[:200]!r}")

        return {'assistant_response': assistant_response}, 200

    except Exception as e:
        # Friendly fallback to avoid frontend crash
        friendly_msg = ("I'm sorry — I couldn't reach the AI service right now. "
                        "Please try again in a moment or simplify your question.")
        print(f"Assistant API Error (stateless): {e}")

        return {'assistant_response': friendly_msg}, 200
