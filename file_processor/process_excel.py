import pandas as pd
import streamlit as st


def process_excel(df):
    """
    Process an Excel file loaded as a pandas DataFrame
    Args:
        df: The DataFrame to process
    Returns:
        DataFrame: The processed DataFrame
    """
    # Excel files might have formatting that we need to handle

    # Check for merged cells (though this won't be detected after loading)
    # Here you would add more specific processing as needed

    # Handle missing values
    missing_values = df.isna().sum().sum()
    if missing_values > 0:
        st.warning(f"Found {missing_values} missing values in the dataset")

    # Return the processed dataframe
    return df


def get_excel_sheets(file):
    """
    Get the sheet names from an Excel file
    Args:
        file: The uploaded file object from Streamlit
    Returns:
        list: The names of the sheets in the Excel file
    """
    try:
        xls = pd.ExcelFile(file)
        return xls.sheet_names
    except Exception as e:
        st.error(f"Error reading Excel sheets: {e}")
        return []


def load_specific_sheet(file, sheet_name):
    """
    Load a specific sheet from an Excel file
    Args:
        file: The uploaded file object from Streamlit
        sheet_name: The name of the sheet to load
    Returns:
        DataFrame: The loaded DataFrame
    """
    try:
        return pd.read_excel(file, sheet_name=sheet_name)
    except Exception as e:
        st.error(f"Error loading sheet {sheet_name}: {e}")
        return None