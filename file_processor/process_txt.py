import pandas as pd
import streamlit as st
from file_loader.utils import detect_delimiter


def process_txt(content):
    """
    Process a text file
    Args:
        content: The content of the text file
    Returns:
        str or DataFrame: The processed content
    """
    # If it's a string, we just return it
    if isinstance(content, str):
        return content

    # If it's a DataFrame, process it like a CSV
    if isinstance(content, pd.DataFrame):
        # Handle missing values
        missing_values = content.isna().sum().sum()
        if missing_values > 0:
            st.warning(f"Found {missing_values} missing values in the dataset")

        return content

    return content


def convert_txt_to_df(text):
    """
    Attempt to convert a text file to a DataFrame
    Args:
        text: The content of the text file
    Returns:
        DataFrame or None: The converted DataFrame or None if conversion failed
    """
    try:
        # Try to detect the delimiter
        delimiter = detect_delimiter(text[:1000])  # Use first 1000 chars as sample

        # Try to convert to DataFrame
        import io
        df = pd.read_csv(io.StringIO(text), delimiter=delimiter)
        return df
    except Exception as e:
        st.warning(f"Could not convert text to DataFrame: {e}")
        return None