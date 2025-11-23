import os
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError
import json
load_dotenv() 

# Get the Gemini API key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize the Gemini client
# Note: The client will automatically use the GEMINI_API_KEY environment variable.
try:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured in .env file.")
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    MODEL = 'gemini-2.5-flash' # A fast and efficient model for summarization
    
except ValueError as e:
    # Handle missing key case gracefully
    print(f"Configuration Error: {e}")
    client = None
except Exception as e:
    print(f"Failed to initialize Gemini Client: {e}")
    client = None

def _api_key_check():
    """Checks if the Gemini client is initialized."""
    if not client:
        return "Error: GEMINI_API_KEY not configured or client failed to initialize."
    return None

def generate_task_summary(description):
    """Generate a concise summary of a task description using the Gemini API."""
    error_check = _api_key_check()
    if error_check:
        return error_check
    
    prompt = f"Summarize this task description in 1-2 concise, clear sentences:\n\n{description}"
    
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )
        return response.text.strip()
    except APIError as e:
        print(f"Gemini API Error: {e}")
        return f"Error: Gemini API call failed. Details: {e}"
    except Exception as e:
        print(f"General Error in concise summarization: {e}")
        return f"Error: An unexpected error occurred. Details: {e}"

def generate_detailed_summary(description):
    """
    Generate a detailed, point-form summary of a task description using the Gemini API.
    Returns a list of summary points.
    """
    error_check = _api_key_check()
    if error_check:
        return [error_check] 
        
    system_instruction = (
        "You are an expert task summarizer. Generate a detailed, point-form summary "
        "of the user's task description. The output MUST be a list of 4-6 bullet points "
        "that provide insights, structure, and break down complex concepts. Do NOT include "
        "any introductory or concluding text, only the bullet points."
    )
    
    prompt = f"Task Description:\n{description}"
    
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        summary_text = response.text.strip()
        
        # Split by newlines, clean up bullet characters, and filter empty strings
        points = [
            point.strip().lstrip('*-').lstrip('•').strip()
            for point in summary_text.split('\n')
            if point.strip()
        ]
        
        return points if points else ["Error: Gemini returned an empty summary or failed to format correctly."]

    except APIError as e:
        print(f"Gemini API Error: {e}")
        return [f"Error: Gemini API call failed. Details: {e}"]
    except Exception as e:
        print(f"General Error in detailed summarization: {e}")
        return [f"Error: An unexpected error occurred. Details: {e}"]
    
    # ... (existing imports and functions) ...

def get_priority_ranking(tasks_data):
    """
    Generates an urgent/important ranking for a list of tasks using the Gemini API.
    This version returns a Markdown table to avoid JSON parsing errors.
    """
    error_check = _api_key_check()
    if error_check:
        # Return error as a dictionary to be handled correctly by the route
        return {'error': error_check, 'ranking_markdown': None}, 500

    # Prepare data as a JSON string to pass context efficiently
    tasks_json = json.dumps(tasks_data, indent=2)

    system_instruction = (
        "You are an expert prioritization engine. Analyze the provided list of tasks, "
        "considering their 'due_date', 'priority', and the content of their 'description' "
        "to determine the optimal working order. Rank the tasks by their **Urgency and Importance**."
        "Your final output MUST be a clean Markdown table with exactly three columns: "
        "'Rank (1, 2, 3..)', 'Task Title', and 'Justification (1 concise sentence).' "
        "Do NOT include any introductory text or conclusions outside the table."
    )

    prompt = f"""
    Rank the following tasks and provide a concise justification for the suggested order.
    
    Task List:
    {tasks_json}

    Return ONLY the Markdown table.
    """

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        # FIX: We now expect and return raw markdown text, not JSON array
        markdown_output = response.text.strip()
        
        if not markdown_output:
             raise ValueError("AI returned an empty response for ranking.")
             
        # Return the clean markdown text
        return {'ranking_markdown': markdown_output, 'message': 'Ranking generated successfully.'}, 200

    except APIError as e:
        print(f"Gemini API Error (Prioritization): {e}")
        return {'error': f"Gemini API call failed during prioritization: {e}"}, 500
    except Exception as e:
        print(f"General Error in prioritization: {e}")
        return {'error': f"An unexpected error occurred during prioritization: {e}"}, 500