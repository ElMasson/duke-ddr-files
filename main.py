import streamlit as st
from styles.jazzy_theme import apply_jazzy_theme
from chat_interface.chat_ui import initialize_chat, display_chat, handle_file_upload, handle_user_input
from data_catalog.crewai_feedback import check_crewai_status


def main():
    # Set page config must be the first Streamlit command
    st.set_page_config(
        page_title="DUKE - Data Cataloging Assistant",
        page_icon="📊",
        layout="wide"
    )

    # Apply jazzy theme
    apply_jazzy_theme()

    # Title
    st.title("DUKE - Data Cataloging Assistant")

    # Initialize chat interface
    initialize_chat()

    # Create a sidebar for file upload
    with st.sidebar:
        st.header("Téléchargement de fichiers")
        handle_file_upload()

        # Add status indicator for CrewAI
        st.markdown("### Status")
        is_running, result, error = check_crewai_status()
        if is_running:
            st.info("Analyse en cours... Veuillez répondre aux demandes de validation quand elles apparaissent.")
        elif error:
            st.error(f"Erreur dans l'analyse: {error}")
        elif result:
            st.success("Analyse terminée avec succès!")

    # Main chat area
    display_chat()

    # Handle user input
    handle_user_input()

    # Check if we need to rerun the app
    if "need_rerun" in st.session_state and st.session_state.need_rerun:
        st.session_state.need_rerun = False
        st.rerun()


if __name__ == "__main__":
    main()