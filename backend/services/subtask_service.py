import json
from ..models.subtask import Subtask
from ..models.task import Task
from ..services.ai_service import client, MODEL, _api_key_check
from google.genai.errors import APIError

def create_subtask_manual(parent_task_id, title, user_id, description=""):
    """Manually create a subtask."""
    new_subtask = Subtask(parent_task_id, title, description, user_id)
    new_subtask.save()
    return {'message': 'Subtask created successfully'}, 201

def get_subtasks_for_task(parent_task_id):
    """Fetch all subtasks for a given parent task."""
    subtasks = Subtask.find_by_parent_id(parent_task_id)
    # Convert ObjectId to string for JSON serialization
    for subtask in subtasks:
        subtask['_id'] = str(subtask['_id'])
        subtask['parent_task_id'] = str(subtask['parent_task_id'])
        subtask['created_at'] = subtask['created_at'].isoformat()
    return subtasks

def mark_subtask_status(subtask_id, status):
    """Mark a subtask as completed or update status."""
    result = Subtask.update_status(subtask_id, status)
    if result.modified_count > 0:
        return {'message': f'Subtask marked as {status}'}, 200
    return {'error': 'Subtask not found'}, 404

def delete_subtask(subtask_id):
    """Delete a single subtask."""
    result = Subtask.delete_by_id(subtask_id)
    if result.deleted_count > 0:
        return {'message': 'Subtask deleted successfully'}, 200
    return {'error': 'Subtask not found'}, 404

# --- AI Subtask Generation (Saves to DB - Used by task_list.html) ---

def generate_subtasks_with_ai(parent_task_id, task_description, user_id):
    """Generates subtasks using the Gemini API, parses them, and saves to the database."""
    error_check = _api_key_check()
    if error_check:
        return {'error': error_check}, 500

    # 💡 FIX: Request a simple numbered list that is easier to parse than JSON
    prompt = f"""Break down the following complex task into 3 to 6 essential and actionable subtasks.
    Provide the output as a simple numbered list (1., 2., 3., etc.). Each subtask must be a single, complete sentence.

    Complex Task: {task_description}
    """

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )
        
        summary_text = response.text.strip()
        
        # 💡 NEW PARSING: Split the text by newline and clean up numbering/whitespace
        raw_points = summary_text.split('\n')
        subtask_list = []
        for point in raw_points:
            # Simple cleanup for common list formats (1., 1) , - , *, etc.)
            clean_title = point.strip()
            if clean_title.startswith(('1.', '2.', '3.', '4.', '5.', '6.')):
                clean_title = clean_title.split('.', 1)[-1].strip()
            elif clean_title.startswith(('-', '*', '•')):
                clean_title = clean_title[1:].strip()
                
            if clean_title:
                subtask_list.append({
                    'title': clean_title,
                    'description': 'AI generated subtask.' # Use a default description
                })

        if not subtask_list:
            raise ValueError("AI failed to return any discernible subtasks.")
            
        # Save each parsed subtask to the database
        saved_titles = []
        for item in subtask_list:
            new_subtask = Subtask(
                parent_task_id, 
                item['title'], 
                item['description'], 
                user_id
            )
            new_subtask.save()
            saved_titles.append(item['title'])

        return {'message': f'Successfully generated and saved {len(saved_titles)} subtasks.', 'subtasks': subtask_list}, 200

    except APIError as e:
        print(f"Gemini API Error (Subtasks): {e}")
        return {'error': f"Gemini API call failed during subtask generation. Details: {e}"}, 500
    except Exception as e:
        print(f"General Error in subtask generation: {e}")
        return {'error': f"An unexpected error occurred during subtask generation: {e}"}, 500

# --- AI Subtask Generation (No DB Save - Used by sandbox page) ---

def generate_subtasks_only(task_description, user_id):
    """Generates subtasks using the Gemini API and returns the markdown text."""
    error_check = _api_key_check()
    if error_check:
        # 💡 FIX: Return error message in 'error' key
        return {'error': error_check}, 500

    # 💡 FIX: Prompt for a clean markdown bullet list
    prompt = f"""Analyze the following task description and break it down into 4-6 detailed, actionable subtasks.
    Return the output as a clean, structured list using markdown bullet points (*).
    
    Complex Task: {task_description}
    """

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )
        
        # 💡 FIX: Return the raw markdown text directly
        markdown_output = response.text.strip()
             
        # Return the generated markdown text directly
        return {'message': 'Subtasks generated successfully.', 'markdown_output': markdown_output}, 200

    except APIError as e:
        print(f"Gemini API Error (Subtasks Sandbox): {e}")
        return {'error': f"Gemini API call failed during subtask generation. Details: {e}"}, 500
    except Exception as e:
        print(f"General Error in subtask sandbox generation: {e}")
        return {'error': f"An unexpected error occurred during subtask generation: {e}"}, 500