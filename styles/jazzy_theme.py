def get_jazzy_colors():
    """
    Returns a dictionary of jazzy colors
    """
    return {
        'background': '#1E1E2E',  # Deep blue-black
        'text': '#E8E6D9',  # Off-white
        'accent1': '#9370DB',  # Medium purple
        'accent2': '#E6AA68',  # Warm gold
        'accent3': '#D84C6F',  # Deep rose
        'accent4': '#5F9EA0',  # Cadet blue
        'gradient1': '#5F4B8B',  # Purple
        'gradient2': '#1E3F66',  # Navy blue
    }


def apply_jazzy_theme():
    """
    Apply the jazzy theme to the Streamlit app
    """
    colors = get_jazzy_colors()

    import streamlit as st

    # Apply custom CSS
    st.markdown(f"""
    <style>
        .reportview-container .main .block-container{{
            max-width: 1200px;
            padding-top: 2rem;
            padding-right: 2rem;
            padding-left: 2rem;
            padding-bottom: 2rem;
        }}
        .reportview-container .main {{
            color: {colors['text']};
            background-color: {colors['background']};
        }}
        .sidebar .sidebar-content {{
            background-color: {colors['background']};
            color: {colors['text']};
        }}
        .Widget>label {{
            color: {colors['text']};
        }}
        .stButton>button {{
            background-color: {colors['accent1']};
            color: {colors['text']};
        }}
        .stTextInput>div>div>input {{
            color: {colors['text']};
        }}
        .stSelectbox>div>div>select {{
            color: {colors['text']};
        }}
        .stFileUploader>div>div>button {{
            background-color: {colors['accent1']};
            color: {colors['text']};
        }}
    </style>
    """, unsafe_allow_html=True)