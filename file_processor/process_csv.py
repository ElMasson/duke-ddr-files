import pandas as pd
import streamlit as st


def process_csv(df):
    """
    Process a CSV file loaded as a pandas DataFrame
    Args:
        df: The DataFrame to process
    Returns:
        DataFrame: The processed DataFrame
    """
    # Perform basic processing
    # Here you would add more specific processing as needed

    # Handle missing values
    missing_values = df.isna().sum().sum()
    if missing_values > 0:
        st.warning(f"Found {missing_values} missing values in the dataset")

    # Return the processed dataframe
    return df


def analyze_csv(df):
    """
    Perform simple analysis on a CSV file
    Args:
        df: The DataFrame to analyze
    Returns:
        dict: Analysis results
    """
    import numpy as np

    # Initialize results
    results = {}

    # Get numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    # Calculate basic statistics for numeric columns
    if len(numeric_cols) > 0:
        results['numeric_stats'] = df[numeric_cols].describe()

    # Get categorical columns
    cat_cols = df.select_dtypes(include=['object', 'category']).columns

    # Calculate value counts for categorical columns
    if len(cat_cols) > 0:
        results['categorical_stats'] = {col: df[col].value_counts() for col in cat_cols}

    return results