import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
import pandas as pd
from file_loader.load_file import load_excel_file, load_csv_file, load_txt_file
from file_loader.utils import get_file_extension

# Load environment variables
load_dotenv()


def get_file_sample(file):
    """Get a sample of the file content for analysis"""
    file_name = file.name
    file_extension = get_file_extension(file_name)

    # Load a small sample of the file for analysis
    try:
        if file_extension in ['.xls', '.xlsx']:
            df = load_excel_file(file)
            if df is not None:
                return df.head(10).to_string()
        elif file_extension == '.csv':
            df = load_csv_file(file)
            if df is not None:
                return df.head(10).to_string()
        elif file_extension == '.txt':
            content = load_txt_file(file)
            if isinstance(content, pd.DataFrame):
                return content.head(10).to_string()
            elif content is not None:
                return content[:1000]  # First 1000 characters
    except Exception as e:
        return f"Error loading file: {str(e)}"

    return "Could not load file content"


def create_multi_agent_catalog_crew(file):
    """
    Create a full multi-agent CrewAI crew for data cataloging.
    This version maintains the multi-agent approach while being compatible with different
    CrewAI versions.

    Args:
        file: The file to catalog

    Returns:
        Crew: The catalog crew with multiple specialized agents
    """
    # Get file sample for analysis
    file_name = file.name
    file_sample = get_file_sample(file)

    # Create specialized agents
    data_analyzer = Agent(
        role="Data Analyst",
        goal="Analyze data files to identify structure, patterns, and quality issues",
        backstory="""You are an expert data analyst with years of experience in 
        understanding various data formats and structures. You excel at identifying 
        patterns, data quality issues, and extracting meaningful insights from raw data.""",
        verbose=True,
        allow_code_execution=True
    )

    data_quality_agent = Agent(
        role="Data Quality Assessor",
        goal="Identify and document data quality issues and propose improvements",
        backstory="""You are a data quality expert who has helped many organizations 
            improve their data. You can quickly spot inconsistencies, missing values, 
            outliers, and other quality issues. You provide clear assessments and 
            actionable recommendations. You run comprehensive code to document precisely the data quality issues""",
        verbose=True,
        allow_delegation=True,
        allow_code_execution=True
    )

    schema_extractor = Agent(
        role="Schema Extractor",
        goal="Extract accurate schema definitions from data files",
        backstory="""You are a database architect specializing in data modeling and 
        schema design. You can look at data and determine the most appropriate data 
        types, relationships, and constraints. You are meticulous and thorough in 
        your analysis.""",
        verbose=True
    )

    metadata_curator = Agent(
        role="Metadata Curator",
        goal="Create comprehensive and accurate metadata descriptions for data assets",
        backstory="""You are a metadata specialist who excels at documenting data assets 
        with rich, meaningful descriptions. You understand how to categorize data, 
        tag it appropriately, and provide context that makes it easily discoverable 
        and usable by others.""",
        verbose=True
    )

    business_glossary_agent = Agent(
        role="Business Glossary Creator",
        goal="Create a comprehensive business glossary with clear definitions",
        backstory="""You are a business analyst who bridges the gap between technical 
        and business domains. You excel at creating clear definitions of business 
        terms and concepts that are understandable to all stakeholders. You ensure 
        consistency in terminology across the organization.""",
        verbose=True
    )

    documentation_agent = Agent(
        role="Documentation Specialist",
        goal="Create comprehensive, clear, and useful documentation for data catalogs",
        backstory="""You are a technical writer with expertise in data documentation. 
        You can transform complex technical details into clear, well-structured 
        documentation that is accessible to both technical and non-technical users. 
        Your documentation is always complete, accurate, and user-friendly.""",
        verbose=True
    )

    # Create tasks for the agents
    # Task 1: Initial file analysis
    file_analysis_task = Task(
        description=f"""
        Analyze the structure and content of the file: {file_name}

        Sample content:
        {file_sample}

        Your task is to:
        1. Identify the overall structure of the file
        2. Determine what kind of data it contains
        3. Identify any patterns or notable features
        4. Provide a summary of what this file appears to be used for

        Be detailed but concise in your analysis.
        Format your output in markdown.

        IMPORTANT: This analysis will be reviewed by a human user for validation.
        """,
        agent=data_analyzer,
        expected_output="A comprehensive analysis of the file structure and content",
        human_input=True
    )

    # Task 2: Schema extraction
    schema_extraction_task = Task(
        description=f"""
        Extract the schema from the file based on the previous analysis.

        File name: {file_name}

        Your task is to:
        1. Define a formal schema for this data
        2. Specify data types for each field/column
        3. Identify primary keys or unique identifiers
        4. Note any foreign key relationships (if multiple tables or files)
        5. Document any constraints or validation rules that should apply
        6. Include any business rules or calculations that apply (e.g., cost = sales - profit)

        Format your schema in a structured, clear markdown format.

        IMPORTANT: This schema extraction will be reviewed by a human user for validation.
        """,
        agent=schema_extractor,
        expected_output="A formal schema definition for the data file",
        human_input=True,
        context=[file_analysis_task]
    )

    # Task 3: Metadata curation
    metadata_task = Task(
        description=f"""
        Create comprehensive metadata for the file based on the analysis and schema extraction.

        File name: {file_name}

        Your task is to:
        1. Create a descriptive title for this data asset
        2. Write a clear description of what this data represents
        3. Suggest relevant tags/keywords for categorization
        4. Define the data domain (e.g., Finance, HR, Marketing)
        5. Document the likely update frequency of this data
        6. Note any sensitivity classifications (e.g., Public, Internal, Confidential)

        Format your metadata in a clear, structured markdown format.

        IMPORTANT: This metadata will be reviewed by a human user for validation.
        """,
        agent=metadata_curator,
        expected_output="Comprehensive metadata for the data file",
        human_input=True,
        context=[schema_extraction_task]
    )

    # Task 4: Data Quality Assessment
    data_quality_task = Task(
        description=f"""
            Assess the quality of data in the file: {file_name}

            Using the schema information and analysis already provided, evaluate the data quality by running dedicated python code to ensure real data output.

            Your task is to:
            1. Evaluate the completeness of the data (missing values, empty fields)
            2. Assess the accuracy and validity of the data
            3. Check for consistency issues (conflicting data)
            4. Identify any outliers or anomalies
            5. Suggest specific improvements to enhance data quality

            Provide a detailed data quality assessment in markdown format.
            """,
        agent=data_quality_agent,
        expected_output="A comprehensive data quality assessment in markdown format",
        context=[file_analysis_task, schema_extraction_task, metadata_task]
        # human_input=True
    )

    # Task 4: Business glossary creation
    glossary_task = Task(
        description=f"""
        Create a business glossary for the key terms in this file based on the previous analysis and metadata.

        File name: {file_name}

        Your task is to:
        1. Identify key business terms/concepts represented in this data
        2. Provide clear definitions for each term
        3. Note any synonyms or related terms
        4. Establish relationships between different terms

        Format your glossary in a clear, structured markdown format.

        IMPORTANT: This business glossary will be reviewed by a human user for validation.
        """,
        agent=business_glossary_agent,
        expected_output="A business glossary for the data file",
        human_input=True,
        context=[metadata_task]
    )

    # Task 5: Final documentation
    documentation_task = Task(
        description=f"""
        Create a comprehensive documentation for the data catalog entry by combining all the previous information.

        File name: {file_name}

        Your task is to:
        1. Integrate the file analysis, schema, metadata, and business glossary into a cohesive document
        2. Ensure all information is organized logically
        3. Highlight the most important aspects users should know
        4. Include any usage examples or common queries

        Format your documentation as a well-structured markdown document.

        IMPORTANT: This final documentation will be reviewed by a human user for validation.
        """,
        agent=documentation_agent,
        expected_output="Comprehensive documentation for the data catalog entry",
        human_input=True,
        context=[file_analysis_task, schema_extraction_task, metadata_task, glossary_task]
    )

    # Create the crew with all agents and tasks
    crew = Crew(
        manager_llm='o3-mini',
        agents=[
            data_analyzer,
            schema_extractor,
            metadata_curator,
            data_quality_agent,
            business_glossary_agent,
            documentation_agent
        ],
        tasks=[
            file_analysis_task,
            schema_extraction_task,
            metadata_task,
            data_quality_task,
            glossary_task,
            documentation_task
        ],
        process=Process.hierarchical,
        verbose=True
    )

    return crew


def run_multi_agent_catalog(file):
    """
    Run the multi-agent catalog process for a file.

    Args:
        file: The file to catalog

    Returns:
        str: The response message
    """
    from data_catalog.crewai_feedback import run_crewai_with_feedback

    # Update status
    message = f"Je commence l'analyse du fichier {file.name} avec une équipe de 5 agents spécialisés CrewAI. Chaque agent a un rôle distinct et vous serez consulté après chaque étape importante."

    # Run the multi-agent catalog process
    result = run_crewai_with_feedback(create_multi_agent_catalog_crew, file)

    return message