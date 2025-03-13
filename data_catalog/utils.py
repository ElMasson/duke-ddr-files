import pandas as pd
import json
from datetime import datetime


def generate_catalog_id(file_name):
    """
    Generate a unique ID for a catalog entry.

    Args:
        file_name: The name of the file

    Returns:
        str: A unique catalog ID
    """
    import hashlib
    import time

    # Generate a hash based on the filename and current timestamp
    timestamp = str(time.time())
    hash_input = file_name + timestamp
    hash_obj = hashlib.md5(hash_input.encode())

    # Return a shortened hash
    return hash_obj.hexdigest()[:12]


def save_catalog_entry(catalog_entry, file_name):
    """
    Save a catalog entry to a JSON file.

    Args:
        catalog_entry: The catalog entry to save
        file_name: The name of the original file

    Returns:
        str: The path to the saved catalog file
    """
    # Generate a filename for the catalog entry
    catalog_id = catalog_entry.get('id', generate_catalog_id(file_name))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    catalog_filename = f"catalog_{catalog_id}_{timestamp}.json"

    # Save the catalog entry
    try:
        with open(catalog_filename, 'w') as file:
            json.dump(catalog_entry, file, indent=2)
        return catalog_filename
    except Exception as e:
        print(f"Error saving catalog entry: {e}")
        return None


def load_catalog_entries():
    """
    Load all saved catalog entries.

    Returns:
        list: A list of catalog entries
    """
    import glob

    catalog_entries = []

    # Find all catalog files
    catalog_files = glob.glob("catalog_*.json")

    # Load each file
    for catalog_file in catalog_files:
        try:
            with open(catalog_file, 'r') as file:
                catalog_entry = json.load(file)
                catalog_entries.append(catalog_entry)
        except Exception as e:
            print(f"Error loading catalog entry {catalog_file}: {e}")

    return catalog_entries


def create_catalog_summary(catalog_entries):
    """
    Create a summary of all catalog entries.

    Args:
        catalog_entries: A list of catalog entries

    Returns:
        DataFrame: A summary DataFrame
    """
    # Create a list of summary dictionaries
    summary_dicts = []

    for entry in catalog_entries:
        summary_dict = {
            'id': entry.get('id', 'unknown'),
            'file_name': entry.get('file_name', 'unknown'),
            'title': entry.get('metadata', {}).get('title', 'unknown'),
            'domain': entry.get('metadata', {}).get('domain', 'unknown'),
            'created_at': entry.get('created_at', 'unknown'),
            'quality_score': entry.get('quality_assessment', {}).get('overall_score', 'unknown')
        }
        summary_dicts.append(summary_dict)

    # Create a DataFrame
    if summary_dicts:
        return pd.DataFrame(summary_dicts)
    else:
        return pd.DataFrame(columns=['id', 'file_name', 'title', 'domain', 'created_at', 'quality_score'])


def export_catalog_to_markdown(catalog_entry):
    """
    Export a catalog entry to a Markdown file.

    Args:
        catalog_entry: The catalog entry to export

    Returns:
        str: The path to the exported Markdown file
    """
    # Extract relevant information
    file_name = catalog_entry.get('file_name', 'unknown')
    catalog_id = catalog_entry.get('id', 'unknown')
    title = catalog_entry.get('metadata', {}).get('title', 'Untitled')
    description = catalog_entry.get('metadata', {}).get('description', 'No description')
    schema = catalog_entry.get('schema', {})
    quality = catalog_entry.get('quality_assessment', {})
    glossary = catalog_entry.get('business_glossary', {})

    # Generate Markdown content
    markdown_content = f"""# Data Catalog: {title}

## Overview
- **File Name:** {file_name}
- **Catalog ID:** {catalog_id}
- **Created At:** {catalog_entry.get('created_at', 'unknown')}

## Description
{description}

## Schema
"""

    # Add schema information
    if isinstance(schema, dict) and 'columns' in schema:
        for column in schema['columns']:
            col_name = column.get('name', 'unknown')
            col_type = column.get('type', 'unknown')
            col_desc = column.get('description', 'No description')

            markdown_content += f"### {col_name}\n"
            markdown_content += f"- **Type:** {col_type}\n"
            markdown_content += f"- **Description:** {col_desc}\n\n"
    else:
        markdown_content += "No schema information available.\n\n"

    # Add quality assessment
    markdown_content += "## Data Quality Assessment\n"
    if isinstance(quality, dict):
        for key, value in quality.items():
            if key != 'overall_score':
                markdown_content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
    else:
        markdown_content += "No quality assessment available.\n"

    # Add business glossary
    markdown_content += "\n## Business Glossary\n"
    if isinstance(glossary, dict) and glossary:
        for term, definition in glossary.items():
            markdown_content += f"### {term}\n{definition}\n\n"
    else:
        markdown_content += "No business glossary available.\n"

    # Generate a filename for the Markdown file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    markdown_filename = f"catalog_{catalog_id}_{timestamp}.md"

    # Save the Markdown file
    try:
        with open(markdown_filename, 'w') as file:
            file.write(markdown_content)
        return markdown_filename
    except Exception as e:
        print(f"Error exporting catalog to Markdown: {e}")
        return None