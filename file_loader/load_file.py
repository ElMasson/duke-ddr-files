import pandas as pd
import streamlit as st


def load_excel_file(file):
    """
    Load an Excel file into a pandas DataFrame
    Args:
        file: The uploaded file object from Streamlit
    Returns:
        DataFrame: The loaded DataFrame
    """
    try:
        return pd.read_excel(file)
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None


def load_csv_file(file, delimiter=','):
    """
    Load a CSV file into a pandas DataFrame
    Args:
        file: The uploaded file object from Streamlit
        delimiter: The delimiter used in the CSV file, defaults to ','
    Returns:
        DataFrame: The loaded DataFrame
    """
    try:
        return pd.read_csv(file, delimiter=delimiter)
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        return None


def load_txt_file(file, delimiter=None):
    """
    Load a text file
    Args:
        file: The uploaded file object from Streamlit
        delimiter: The delimiter to use if parsing as structured data
    Returns:
        str or DataFrame: The content of the file
    """
    try:
        # First try to read as text
        content = file.read().decode('utf-8')

        # If delimiter is provided, try to parse as CSV
        if delimiter:
            import io
            return pd.read_csv(io.StringIO(content), delimiter=delimiter)

        return content
    except Exception as e:
        st.error(f"Error loading text file: {e}")
        return None