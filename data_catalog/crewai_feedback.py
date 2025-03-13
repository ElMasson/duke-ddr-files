import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
import threading
import queue

# Load environment variables
load_dotenv()

# Global feedback queue system
feedback_queue = queue.Queue()
next_step_event = threading.Event()


def get_human_input(prompt):
    """
    Custom function for getting human input in Streamlit context.
    This is the function that will be used by CrewAI when a task has human_input=True.

    Args:
        prompt: The prompt from CrewAI requesting human feedback

    Returns:
        str: The human feedback
    """
    # Parse the prompt to get a cleaner version
    if "HUMAN FEEDBACK" in prompt:
        parts = prompt.split("=====")
        if len(parts) >= 2:
            prompt = parts[1].strip()

    # Update the chat with the feedback request
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"## Validation requise\n\n{prompt}\n\nVeuillez valider ou fournir des corrections."
    })

    # Update the workflow stage to indicate waiting for feedback
    st.session_state.workflow_stage = "awaiting_feedback"

    # Set the prompt in session state for reference
    st.session_state.current_feedback_prompt = prompt

    # Signal need to rerun to update UI
    st.session_state.need_rerun = True

    # Wait for feedback to be provided
    # This is a blocking call in the CrewAI thread
    feedback = feedback_queue.get()

    # Signal that we can proceed to the next step
    next_step_event.set()

    return feedback


def provide_feedback(feedback):
    """
    Function to be called from the UI when the user provides feedback.

    Args:
        feedback: The feedback provided by the user
    """
    # Put the feedback in the queue
    feedback_queue.put(feedback)

    # Update workflow stage
    st.session_state.workflow_stage = "processing_feedback"

    # Add user feedback to message history
    st.session_state.messages.append({
        "role": "user",
        "content": feedback
    })

    # Add a response indicating feedback received
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Merci pour votre feedback. Je continue avec l'analyse."
    })


def run_crewai_with_feedback(create_crew_func, *args, **kwargs):
    """
    Run a CrewAI crew with human feedback integration.

    Args:
        create_crew_func: Function that creates and returns a CrewAI crew
        *args, **kwargs: Arguments to pass to the create_crew_func

    Returns:
        The result from the CrewAI crew
    """
    # Override the CrewAI human_input function with our Streamlit-compatible version
    # This is a bit of a hack, but necessary to integrate with Streamlit
    import crewai.agents.cache
    original_func = crewai.agents.cache.get_human_input
    crewai.agents.cache.get_human_input = get_human_input

    # Create crew
    crew = create_crew_func(*args, **kwargs)

    # Create and start thread
    def run_crew():
        try:
            result = crew.kickoff()
            # Store result in session state
            st.session_state.crewai_result = result
        except Exception as e:
            # Store error in session state
            st.session_state.crewai_error = str(e)
        finally:
            # Restore original function
            crewai.agents.cache.get_human_input = original_func

    crew_thread = threading.Thread(target=run_crew)
    crew_thread.daemon = True
    crew_thread.start()

    # Store thread in session state
    st.session_state.crew_thread = crew_thread

    # Return immediately, actual result will be available later in session state
    return "Processing started. You will be prompted for feedback as needed."


def check_crewai_status():
    """
    Check if the CrewAI thread is still running and if there are results.

    Returns:
        tuple: (is_running, result, error)
    """
    if "crew_thread" not in st.session_state:
        return False, None, None

    thread = st.session_state.crew_thread
    is_running = thread.is_alive()
    result = st.session_state.get("crewai_result", None)
    error = st.session_state.get("crewai_error", None)

    return is_running, result, error