import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import CodeInterpreterTool
import pandas as pd
import streamlit as st
from file_loader.load_file import load_excel_file, load_csv_file, load_txt_file
from file_loader.utils import get_file_extension
import time
import agentops


# Load environment variables
load_dotenv()


#init agentops
agentops.init(api_key="7c70392b-f574-456d-aa56-1196d9d1c5b8",
    default_tags=['crewai'])

def create_catalog_crew(file):
    """
    Create a real CrewAI crew for data cataloging.

    Args:
        file: The file to catalog

    Returns:
        Crew: The catalog crew
    """
    # Initialize the tool
    code_interpreter = CodeInterpreterTool(unsafe_mode=True)

    # Create the agents
    data_analyzer = Agent(
        role="Data Analyst",
        goal="Analyze data files to identify structure, patterns, and quality issues",
        backstory="""You are an expert data analyst with years of experience in 
        understanding various data formats and structures. You excel at identifying 
        patterns, data quality issues, and extracting meaningful insights from raw data.
        You can run code to already provide high level data analysis at the data catalogue creation""",
        verbose=True,
        allow_delegation=True,
        allow_code_execution=True  # This automatically adds the CodeInterpreterTool
    )

    schema_extractor = Agent(
        role="Schema Extractor",
        goal="Extract accurate schema definitions from data files",
        backstory="""You are a database architect specializing in data modeling and 
        schema design. You can look at data and determine the most appropriate data 
        types, relationships, and constraints. You are meticulous and thorough in 
        your analysis.""",
        verbose=True,
        allow_delegation=True
    )

    metadata_curator = Agent(
        role="Metadata Curator",
        goal="Create comprehensive and accurate metadata descriptions for data assets",
        backstory="""You are a metadata specialist who excels at documenting data assets 
        with rich, meaningful descriptions. You understand how to categorize data, 
        tag it appropriately, and provide context that makes it easily discoverable 
        and usable by others.""",
        verbose=True,
        allow_delegation=True
    )

    data_quality_agent = Agent(
        role="Data Quality Assessor",
        goal="Identify and document data quality issues and propose improvements",
        backstory="""You are a data quality expert who has helped many organizations 
        improve their data. You can quickly spot inconsistencies, missing values, 
        outliers, and other quality issues. You provide clear assessments and 
        actionable recommendations. You run comprehensive code to document precisely the data quality issues""",
        verbose=True,
        allow_delegation=False,
        allow_code_execution=True # This automatically adds the CodeInterpreterTool
    )

    business_glossary_agent = Agent(
        role="Business Glossary Creator",
        goal="Create a comprehensive business glossary with clear definitions",
        backstory="""You are a business analyst who bridges the gap between technical 
        and business domains. You excel at creating clear definitions of business 
        terms and concepts that are understandable to all stakeholders. You ensure 
        consistency in terminology across the organization.""",
        verbose=True,
        allow_delegation=True
    )

    documentation_agent = Agent(
        role="Documentation Specialist",
        goal="Create comprehensive, clear, and useful documentation for data catalogs",
        backstory="""You are a technical writer with expertise in data documentation. 
        You can transform complex technical details into clear, well-structured 
        documentation that is accessible to both technical and non-technical users. 
        Your documentation is always complete, accurate, and user-friendly.""",
        verbose=True,
        allow_delegation=True
    )

    # Create tasks with human_input=True for validation at each step
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

    # Task 1: File Analysis
    file_analysis_task = Task(
        description=f"""
        Analyze the structure and content of the file: {file_name}

        Sample content:
        {file_content}

        Your task is to:
        1. Identify the overall structure of the file
        2. Determine what kind of data it contains
        3. Identify any patterns or notable features
        4. Provide a summary of what this file appears to be used for

        Be detailed but concise in your analysis. Run code to create high level input already on the data catalogue curation
        """,
        agent=data_analyzer,
        expected_output="A comprehensive analysis of the file structure and content in markdown format"
        #human_input=True
    )

    # Task 2: Schema Extraction
    schema_extraction_task = Task(
        description=f"""
        Extract the schema from the file: {file_name}

        Based on the previous analysis and the sample data, create a formal schema definition.

        Your task is to:
        0. Identify if the table in tabular shape or in other style. Provide guidelines to clean the dataset into a tabular format fit for analysis. 
        1. Define a formal schema for this data
        2. Specify data types for each field/column
        3. Identify primary keys or unique identifiers
        4. Note any foreign key relationships (if multiple tables or files)
        5. Document any constraints or validation rules that should apply to this data
        6. Include any business rules or calculations that apply (e.g., cost = sales - profit)

        Provide the schema in a structured, clear format using markdown.
        """,
        agent=schema_extractor,
        expected_output="A formal schema definition for the data file in markdown format",
        context=[file_analysis_task]
        #human_input=True
    )

    # Task 3: Metadata Curation
    metadata_curation_task = Task(
        description=f"""
        Create comprehensive metadata for the file: {file_name}

        Using the schema information and analysis already provided, create detailed metadata.

        Your task is to:
        1. Create a descriptive title for this data asset
        2. Write a clear description of what this data represents
        3. Suggest relevant tags/keywords for categorization
        4. Define the data domain (e.g., Finance, HR, Marketing)
        5. Document the likely update frequency of this data
        6. Note any sensitivity classifications (e.g., Public, Internal, Confidential)
        7. Note all fields that can fall under GDPR considerations

        Create metadata that would help users discover and understand this data asset.

        IMPORTANT: Check with the human user if your metadata is appropriate and if they want to add any additional information.
        """,
        agent=metadata_curator,
        expected_output="Comprehensive metadata for the data file in markdown format",
        context=[schema_extraction_task]
        #human_input=True
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
        

        IMPORTANT: Check with the human user if your quality assessment is thorough enough and if they have additional quality concerns.
        """,
        agent=data_quality_agent,
        expected_output="A comprehensive data quality assessment in markdown format",
        context=[file_analysis_task, schema_extraction_task, metadata_curation_task]
        #human_input=True
    )

    # Task 5: Business Glossary
    business_glossary_task = Task(
        description=f"""
        Create a business glossary based on the data in {file_name}

        Using all the information collected so far (analysis, schema, metadata, quality assessment),
        create a comprehensive business glossary.

        Your task is to:
        1. Identify key business terms/concepts represented in this data
        2. Provide clear definitions for each term
        3. Note any synonyms or related terms
        4. Establish relationships between different terms
        5. Ensure consistency with any existing business terminology

        Create a business glossary that would help users understand the business context of this data.
        Format your response in markdown.

        IMPORTANT: Check with the human user if your business glossary is accurate and if they want to add or modify any definitions.
        """,
        agent=business_glossary_agent,
        expected_output="A business glossary for the data file in markdown format",
        context=[metadata_curation_task]
        #human_input=True
    )

    # Task 6: Documentation
    documentation_task = Task(
        description=f"""
        Create comprehensive documentation for the data catalog entry for: {file_name}

        Compile all the information collected so far into a well-structured documentation.

        Your task is to:
        1. Create a well-structured, comprehensive data catalog entry
        2. Ensure all important information is included and organized logically
        3. Write in a clear, concise style accessible to both technical and business users
        4. Highlight the most important aspects that users should know about this data
        5. Include any usage examples or common queries that might be useful

        The documentation should serve as a complete reference for this data asset.
        Format your response in markdown.

        
        """,
        agent=documentation_agent,
        expected_output="Comprehensive documentation for the data catalog entry in markdown format",
        context=[file_analysis_task, schema_extraction_task,data_quality_task, metadata_curation_task, business_glossary_task]

        #human_input=True
    )

    # Task 7: Documentation
    yaml_catalog_task = Task(
        description=f"""
           Create comprehensive documentation for the data catalog entry for: {file_name}

           Compile all the information collected so far into a well-structured documentation.

           Your task is to:
           1. Create a well-structured, comprehensive data catalog entry
           2. Ensure all important information is included and organized logically
           3. Write in a clear, concise style accessible to both technical and business users
           4. Highlight the most important aspects that users should know about this data
           5. Include any usage examples or common queries that might be useful

           The documentation should serve as a complete reference for this data asset that will be used as input for future LLM powered data analysis.
           Format your response in yaml. It should only have relevant informations for the future task and therefore less decorators than the human ready catalogu


           """,
        agent=documentation_agent,
        expected_output="Comprehensive documentation for the data catalog entry in yaml format designed for future LLM input for exceptional data analysis",
        context=[documentation_task]

        # human_input=True
    )

    manager = Agent(
        role="Senior Data Stewart",
        goal="Efficiently manage the crew and ensure high-quality data gouvernance and definition by all team members",
        backstory="You're an experienced  Data Stewart, skilled in overseeing complex data gouverance and documentation projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed on time and to the highest standard.",
        allow_delegation=True,
    )
    # Create the crew
    crew = Crew(
        manager_llm='o3-mini',
        #manager_agent=manager,
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
            metadata_curation_task,
            data_quality_task,
            business_glossary_task,
            documentation_task
#            yaml_catalog_task
        ],
        process=Process.hierarchical,
        verbose=True
    )

    return crew


def run_catalog_crew(file):
    """
    Run the CrewAI catalog process for a file.

    Args:
        file: The file to catalog

    Returns:
        str: The final catalog documentation
    """
    # Update status
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"Je commence l'analyse du fichier {file.name} avec CrewAI. Vous serez consulté à chaque étape du processus."
    })

    # Create and run the crew
    crew = create_catalog_crew(file)
    result = crew.kickoff()

    # Update with final result
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"Le catalogue de données pour {file.name} est maintenant complet:\n\n{result}"
    })

    return result