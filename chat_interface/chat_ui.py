import streamlit as st
from file_loader.utils import is_valid_file_type
from file_processor.utils import get_file_stats
import os


def initialize_chat():
    """
    Initialize the chat interface in Streamlit.
    Sets up the session state for messages and uploaded files.
    """
    # Initialize session state for chat messages if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant",
             "content": "Bonjour ! Je suis votre assistant pour le catalogage de données. Vous pouvez télécharger vos fichiers ici pour commencer l'analyse."}
        ]

    # Initialize session state for uploaded files if not exists
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    # Initialize session state for current workflow stage
    if "workflow_stage" not in st.session_state:
        st.session_state.workflow_stage = "initial"

    # Initialize session state for processed files to track which files have been processed
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = set()


def display_chat():
    """
    Display the chat interface with message history.
    """
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_file_upload():
    """
    Handle file upload through the chat interface.
    """
    # Process uploaded files
    uploaded_files = st.file_uploader(
        "Déposez vos fichiers ici",
        type=['xls', 'xlsx', 'csv', 'txt'],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    # Check if new files have been uploaded
    if uploaded_files and set(f.name for f in uploaded_files) != set(f.name for f in st.session_state.uploaded_files):
        # Store new uploaded files in session state
        st.session_state.uploaded_files = uploaded_files

        # Add message about uploaded files
        file_names = [file.name for file in uploaded_files]
        user_message = f"J'ai téléchargé les fichiers suivants: {', '.join(file_names)}"
        st.session_state.messages.append({"role": "user", "content": user_message})

        # Add initial system response
        file_stats = []
        for file in uploaded_files:
            stats = get_file_stats(file)
            file_stats.append(f"- {stats['name']} ({stats['type']}, {stats['size_human']})")

        assistant_response = (
            f"Merci d'avoir téléchargé ces fichiers. Voici les détails:\n\n"
            f"{chr(10).join(file_stats)}\n\n"
            f"Je vais maintenant commencer à analyser ces fichiers pour créer un catalogue de données. "
            f"Je vous tiendrai informé à chaque étape."
        )
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

        # Update workflow stage
        st.session_state.workflow_stage = "files_uploaded"

        # Rerun the app to update the chat
        st.rerun()

    # Check if we need to start the workflow
    if (st.session_state.workflow_stage == "files_uploaded" and
            uploaded_files and
            any(file.name not in st.session_state.processed_files for file in uploaded_files)):

        # Get only new files that haven't been processed
        new_files = [file for file in uploaded_files if file.name not in st.session_state.processed_files]

        if new_files:
            # Mark all files as processed
            for file in new_files:
                st.session_state.processed_files.add(file.name)

            # Start the cataloging workflow using CrewAI
            st.session_state.workflow_stage = "analysis_started"

            # Import here to avoid circular imports
            from data_catalog.crewai_catalog import run_catalog_crew

            # Start CrewAI workflow for the first file
            run_catalog_crew(new_files[0])

            # Force a rerun to update the UI
            st.rerun()


def handle_user_input():
    """
    Handle user input from the chat interface.
    """
    # Get user input
    if prompt := st.chat_input("Posez une question ou donnez des instructions..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process user input based on current workflow stage
        process_user_input(prompt)


def process_user_input(prompt):
    """
    Process user input based on current workflow stage.
    Args:
        prompt: The user's input text
    """
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        # Process based on workflow stage
        if st.session_state.workflow_stage == "initial":
            response = "Veuillez télécharger des fichiers pour commencer l'analyse."

        elif st.session_state.workflow_stage == "files_uploaded":
            # This shouldn't happen normally as workflow should start automatically
            # But just in case, we handle it here
            from data_catalog.crewai_catalog import create_catalog_crew
            from data_catalog.crewai_feedback import run_crewai_with_feedback

            response = "Je commence l'analyse des fichiers avec CrewAI. Je vous demanderai votre validation à chaque étape importante."
            message_placeholder.markdown(response)

            # Start the cataloging workflow with CrewAI
            st.session_state.workflow_stage = "analysis_started"

            # Get the first file
            if st.session_state.uploaded_files:
                file = st.session_state.uploaded_files[0]

                # Run CrewAI with feedback
                run_crewai_with_feedback(create_catalog_crew, file)

            # Rerun to update the UI
            st.session_state.need_rerun = True
            return

        elif st.session_state.workflow_stage == "awaiting_feedback":
            # Get feedback from user and provide it to CrewAI
            from data_catalog.crewai_feedback import provide_feedback

            # Provide the feedback to CrewAI
            provide_feedback(prompt)

            # The response will be added in the provide_feedback function
            return

        else:
            response = "Je continue l'analyse. Je reviendrai vers vous dès que j'aurai besoin de votre validation."

        # Update the message placeholder
        message_placeholder.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})