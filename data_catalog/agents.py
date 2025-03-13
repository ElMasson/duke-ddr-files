from crewai import Agent
from langchain_community.llms import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


def get_llm():
    """
    Get the language model to use with the agents.
    Returns:
        LLM: The language model
    """
    # Use OpenAI's model
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")

        return OpenAI(api_key=api_key, temperature=0.2)
    except Exception as e:
        # Fallback to a local model or dummy implementation
        print(f"Error loading OpenAI model: {e}")
        # Return a dummy model for development
        from langchain.llms.fake import FakeListLLM
        return FakeListLLM(responses=["This is a dummy response."])


def create_data_analyzer_agent():
    """
    Create an agent responsible for analyzing data files.
    Returns:
        Agent: The data analyzer agent
    """
    return Agent(
        role="Data Analyst",
        goal="Analyze data files to identify structure, patterns, and quality issues",
        backstory="""You are an expert data analyst with years of experience in 
        understanding various data formats and structures. You excel at identifying 
        patterns, data quality issues, and extracting meaningful insights from raw data.""",
        llm=get_llm(),
        verbose=True
    )


def create_schema_extractor_agent():
    """
    Create an agent responsible for extracting the schema from data files.
    Returns:
        Agent: The schema extractor agent
    """
    return Agent(
        role="Schema Extractor",
        goal="Extract accurate schema definitions from data files",
        backstory="""You are a database architect specializing in data modeling and 
        schema design. You can look at data and determine the most appropriate data 
        types, relationships, and constraints. You are meticulous and thorough in 
        your analysis.""",
        llm=get_llm(),
        verbose=True
    )


def create_metadata_curator_agent():
    """
    Create an agent responsible for curating metadata.
    Returns:
        Agent: The metadata curator agent
    """
    return Agent(
        role="Metadata Curator",
        goal="Create comprehensive and accurate metadata descriptions for data assets",
        backstory="""You are a metadata specialist who excels at documenting data assets 
        with rich, meaningful descriptions. You understand how to categorize data, 
        tag it appropriately, and provide context that makes it easily discoverable 
        and usable by others.""",
        llm=get_llm(),
        verbose=True
    )


def create_data_quality_agent():
    """
    Create an agent responsible for assessing data quality.
    Returns:
        Agent: The data quality agent
    """
    return Agent(
        role="Data Quality Assessor",
        goal="Identify and document data quality issues and propose improvements",
        backstory="""You are a data quality expert who has helped many organizations 
        improve their data. You can quickly spot inconsistencies, missing values, 
        outliers, and other quality issues. You provide clear assessments and 
        actionable recommendations.""",
        llm=get_llm(),
        verbose=True
    )


def create_business_glossary_agent():
    """
    Create an agent responsible for building a business glossary.
    Returns:
        Agent: The business glossary agent
    """
    return Agent(
        role="Business Glossary Creator",
        goal="Create a comprehensive business glossary with clear definitions",
        backstory="""You are a business analyst who bridges the gap between technical 
        and business domains. You excel at creating clear definitions of business 
        terms and concepts that are understandable to all stakeholders. You ensure 
        consistency in terminology across the organization.""",
        llm=get_llm(),
        verbose=True
    )


def create_documentation_agent():
    """
    Create an agent responsible for generating comprehensive documentation.
    Returns:
        Agent: The documentation agent
    """
    return Agent(
        role="Documentation Specialist",
        goal="Create comprehensive, clear, and useful documentation for data catalogs",
        backstory="""You are a technical writer with expertise in data documentation. 
        You can transform complex technical details into clear, well-structured 
        documentation that is accessible to both technical and non-technical users. 
        Your documentation is always complete, accurate, and user-friendly.""",
        llm=get_llm(),
        verbose=True
    )