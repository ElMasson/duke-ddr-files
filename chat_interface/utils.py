import streamlit as st
from styles.jazzy_theme import get_jazzy_colors


def format_message(message, message_type="info"):
    """
    Format a message with the appropriate styling based on message type.
    Args:
        message: The message to format
        message_type: The type of message (info, success, warning, error)
    Returns:
        str: HTML formatted message
    """
    colors = get_jazzy_colors()

    if message_type == "success":
        background_color = "#2E7D32"
        text_color = "#FFFFFF"
    elif message_type == "warning":
        background_color = "#FF9800"
        text_color = "#000000"
    elif message_type == "error":
        background_color = "#C62828"
        text_color = "#FFFFFF"
    else:  # info
        background_color = colors['accent1']
        text_color = colors['text']

    return f"""
    <div style="
        background-color: {background_color};
        color: {text_color};
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0px;
    ">
        {message}
    </div>
    """


def display_catalog_progress(stage, progress_value):
    """
    Display a progress bar for the cataloging process.
    Args:
        stage: Current stage description
        progress_value: Progress value between 0 and 1
    """
    st.markdown(f"**Étape actuelle:** {stage}")
    st.progress(progress_value)


def update_chat_with_catalog_progress(stage, details=None):
    """
    Update the chat with the current cataloging progress.
    Args:
        stage: Current stage description
        details: Optional details to display
    """
    message = f"**Mise à jour du catalogue:** {stage}"
    if details:
        message += f"\n\n{details}"

    # Only add to message history, don't try to display directly
    st.session_state.messages.append({"role": "assistant", "content": message})

    # Flag to indicate a rerun is needed
    if "need_rerun" not in st.session_state:
        st.session_state.need_rerun = True