import streamlit as st
import pandas as pd
from styles.utils import format_dataframe


def display_dataframe(df, title=None):
    """
    Display a pandas DataFrame with streamlit
    Args:
        df: The DataFrame to display
        title: The title to display above the DataFrame
    """
    if title:
        st.subheader(title)

    # Apply jazzy styling
    styled_df = format_dataframe(df)
    st.dataframe(styled_df)


def display_text(text, title=None):
    """
    Display text with streamlit
    Args:
        text: The text to display
        title: The title to display above the text
    """
    if title:
        st.subheader(title)
    st.text_area("", text, height=300)


def display_file_summary(df):
    """
    Display a summary of the loaded file
    Args:
        df: The DataFrame to summarize
    """
    st.write("### File Summary")

    # Create summary dataframe
    summary = pd.DataFrame({
        'Column': df.columns,
        'Type': df.dtypes,
        'Non-Null Count': df.count(),
        'Null Count': df.isna().sum(),
        'Unique Values': [df[col].nunique() for col in df.columns]
    })

    # Display summary
    styled_summary = format_dataframe(summary)
    st.dataframe(styled_summary)