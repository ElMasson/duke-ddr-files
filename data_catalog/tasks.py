from crewai import Task
import pandas as pd
import streamlit as st
from file_loader.load_file import load_excel_file, load_csv_file, load_txt_file
from file_loader.utils import get_file_extension
from chat_interface.utils import update_chat_with_catalog_progress


def create_file_analysis_task(data_analyzer, file):
    """
    Create a task for analyzing a file's structure and content.

    Args:
        data_analyzer: The data analyzer agent
        file: The file to analyze

    Returns:
        Task: The file analysis task
    """
    # Prepare file info
    file_name = file.name
    file_extension = get_file_extension(file_name)

    # Load a small sample of the file for analysis
    file_content = None
    try:
        if file_extension in ['.xls', '.xlsx']:
            df = load_excel_file(file)
            if df is not None:
                file_content = df.head(10).to_string()
        elif file_extension == '.csv':
            df = load_csv_file(file)
            if df is not None:
                file_content = df.head(10).to_string()
        elif file_extension == '.txt':
            file_content = load_txt_file(file)
            if isinstance(file_content, pd.DataFrame):
                file_content = file_content.head(10).to_string()
            elif file_content is not None:
                file_content = file_content[:1000]  # First 1000 characters
    except Exception as e:
        file_content = f"Error loading file: {str(e)}"

    # Create the task
    return Task(
        description=f"""
        Analyze the structure and content of the file: {file_name}

        Sample content:
        {file_content}

        Your task is to:
        1. Identify the overall structure of the file
        2. Determine what kind of data it contains
        3. Identify any patterns or notable features
        4. Provide a summary of what this file appears to be used for

        Be detailed but concise in your analysis.
        """,
        agent=data_analyzer,
        expected_output="A comprehensive analysis of the file structure and content",
        async_execution=False
    )


def create_schema_extraction_task(schema_extractor, file, file_analysis_result):
    """
    Create a task for extracting the schema from a file.

    Args:
        schema_extractor: The schema extractor agent
        file: The file to extract schema from
        file_analysis_result: The result of the file analysis task

    Returns:
        Task: The schema extraction task
    """
    # Prepare file info
    file_name = file.name
    file_extension = get_file_extension(file_name)

    # Load a sample of the file for schema extraction
    schema_info = "Could not load schema information"
    try:
        if file_extension in ['.xls', '.xlsx', '.csv']:
            df = None
            if file_extension in ['.xls', '.xlsx']:
                df = load_excel_file(file)
            else:
                df = load_csv_file(file)

            if df is not None:
                # Create schema information string
                columns_info = []
                for col in df.columns:
                    dtype = str(df[col].dtype)
                    non_null = df[col].count()
                    unique_values = df[col].nunique()
                    sample_values = df[col].dropna().head(3).tolist()

                    columns_info.append(
                        f"Column: {col}\n"
                        f"  - Data Type: {dtype}\n"
                        f"  - Non-Null Count: {non_null}/{len(df)}\n"
                        f"  - Unique Values: {unique_values}\n"
                        f"  - Sample Values: {sample_values}"
                    )

                schema_info = "\n".join(columns_info)
        elif file_extension == '.txt':
            schema_info = "Text file - structured schema not applicable"
    except Exception as e:
        schema_info = f"Error extracting schema: {str(e)}"

    # Create the task
    return Task(
        description=f"""
        Extract the schema from the file: {file_name}

        Previous analysis:
        {file_analysis_result}

        Schema information:
        {schema_info}

        Your task is to:
        1. Define a formal schema for this data
        2. Specify data types for each field/column
        3. Identify primary keys or unique identifiers
        4. Note any foreign key relationships (if multiple tables or files)
        5. Document any constraints or validation rules that should apply to this data

        Provide the schema in a structured, clear format.
        """,
        agent=schema_extractor,
        expected_output="A formal schema definition for the data file",
        async_execution=False
    )


def create_metadata_curation_task(metadata_curator, file, schema_result):
    """
    Create a task for curating metadata for a file.

    Args:
        metadata_curator: The metadata curator agent
        file: The file to create metadata for
        schema_result: The result of the schema extraction task

    Returns:
        Task: The metadata curation task
    """
    return Task(
        description=f"""
        Create comprehensive metadata for the file: {file.name}

        Schema information:
        {schema_result}

        Your task is to:
        1. Create a descriptive title for this data asset
        2. Write a clear description of what this data represents
        3. Suggest relevant tags/keywords for categorization
        4. Define the data domain (e.g., Finance, HR, Marketing)
        5. Document the likely update frequency of this data
        6. Note any sensitivity classifications (e.g., Public, Internal, Confidential)

        Create metadata that would help users discover and understand this data asset.
        """,
        agent=metadata_curator,
        expected_output="Comprehensive metadata for the data file",
        async_execution=False
    )


def create_data_quality_assessment_task(data_quality_agent, file, schema_result):
    """
    Create a task for assessing the quality of data in a file.

    Args:
        data_quality_agent: The data quality agent
        file: The file to assess
        schema_result: The result of the schema extraction task

    Returns:
        Task: The data quality assessment task
    """
    # Prepare file info
    file_name = file.name
    file_extension = get_file_extension(file_name)

    # Load file for quality assessment
    quality_info = "Could not load data for quality assessment"
    try:
        df = None
        if file_extension in ['.xls', '.xlsx']:
            df = load_excel_file(file)
        elif file_extension == '.csv':
            df = load_csv_file(file)
        elif file_extension == '.txt':
            content = load_txt_file(file)
            if isinstance(content, pd.DataFrame):
                df = content

        if df is not None:
            # Calculate quality metrics
            missing_values = df.isna().sum().sum()
            duplicate_rows = df.duplicated().sum()
            total_rows = len(df)

            quality_info = (
                f"Total rows: {total_rows}\n"
                f"Missing values: {missing_values}\n"
                f"Duplicate rows: {duplicate_rows}\n"
            )
    except Exception as e:
        quality_info = f"Error assessing data quality: {str(e)}"

    # Create the task
    return Task(
        description=f"""
        Assess the quality of data in the file: {file_name}

        Schema information:
        {schema_result}

        Quality metrics:
        {quality_info}

        Your task is to:
        1. Evaluate the completeness of the data (missing values, empty fields)
        2. Assess the accuracy and validity of the data
        3. Check for consistency issues (conflicting data)
        4. Identify any outliers or anomalies
        5. Suggest specific improvements to enhance data quality

        Provide a detailed data quality assessment.
        """,
        agent=data_quality_agent,
        expected_output="A comprehensive data quality assessment",
        async_execution=False
    )


def create_business_glossary_task(business_glossary_agent, schema_result, metadata_result):
    """
    Create a task for building a business glossary based on the file.

    Args:
        business_glossary_agent: The business glossary agent
        schema_result: The result of the schema extraction task
        metadata_result: The result of the metadata curation task

    Returns:
        Task: The business glossary task
    """
    return Task(
        description=f"""
        Create a business glossary based on the data schema and metadata.

        Schema information:
        {schema_result}

        Metadata:
        {metadata_result}

        Your task is to:
        1. Identify key business terms/concepts represented in this data
        2. Provide clear definitions for each term
        3. Note any synonyms or related terms
        4. Establish relationships between different terms
        5. Ensure consistency with any existing business terminology

        Create a business glossary that would help users understand the business context of this data.
        """,
        agent=business_glossary_agent,
        expected_output="A business glossary for the data file",
        async_execution=False
    )


def create_documentation_task(documentation_agent, file, analysis_result, schema_result, metadata_result,
                              quality_result, glossary_result):
    """
    Create a task for generating comprehensive documentation for a file.

    Args:
        documentation_agent: The documentation agent
        file: The file to document
        analysis_result: The result of the file analysis task
        schema_result: The result of the schema extraction task
        metadata_result: The result of the metadata curation task
        quality_result: The result of the data quality assessment task
        glossary_result: The result of the business glossary task

    Returns:
        Task: The documentation task
    """
    return Task(
        description=f"""
        Create comprehensive documentation for the data catalog entry for: {file.name}

        Compile all the information collected so far:

        File Analysis:
        {analysis_result}

        Schema:
        {schema_result}

        Metadata:
        {metadata_result}

        Data Quality Assessment:
        {quality_result}

        Business Glossary:
        {glossary_result}

        Your task is to:
        1. Create a well-structured, comprehensive data catalog entry
        2. Ensure all important information is included and organized logically
        3. Write in a clear, concise style accessible to both technical and business users
        4. Highlight the most important aspects that users should know about this data
        5. Include any usage examples or common queries that might be useful

        The documentation should serve as a complete reference for this data asset.
        """,
        agent=documentation_agent,
        expected_output="Comprehensive documentation for the data catalog entry",
        async_execution=False
    )


def get_user_validation(stage, result):
    """
    Get validation from the user for a specific stage result.

    Args:
        stage: The stage being validated
        result: The result to validate

    Returns:
        bool: True if the user validated the result, False otherwise
    """
    # Update the chat with the validation request
    update_chat_with_catalog_progress(
        f"Validation requise: {stage}",
        f"Voici le résultat de l'étape '{stage}':\n\n{result}\n\nVeuillez valider ce résultat ou suggérer des modifications."
    )

    # Update workflow stage to await validation
    st.session_state.workflow_stage = "awaiting_validation"

    # Wait for user response (handled in the main loop)
    return True  # Placeholder - actual validation is handled asynchronously