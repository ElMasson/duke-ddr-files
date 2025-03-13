def get_file_extension(file_name):
    """
    Get the extension of a file
    Args:
        file_name: The name of the file
    Returns:
        str: The extension of the file
    """
    import os
    return os.path.splitext(file_name)[1].lower()


def is_valid_file_type(file_name):
    """
    Check if the file type is valid
    Args:
        file_name: The name of the file
    Returns:
        bool: True if the file type is valid, False otherwise
    """
    valid_extensions = ['.xls', '.xlsx', '.csv', '.txt']
    return get_file_extension(file_name) in valid_extensions


def detect_delimiter(sample_text):
    """
    Attempt to detect the delimiter in a text file
    Args:
        sample_text: A sample of the text file
    Returns:
        str: The detected delimiter
    """
    import csv
    from io import StringIO

    potential_delimiters = [',', ';', '\t', '|']
    max_count = 0
    max_delimiter = ','

    for delimiter in potential_delimiters:
        sample = StringIO(sample_text)
        try:
            reader = csv.reader(sample, delimiter=delimiter)
            row = next(reader)
            count = len(row)
            if count > max_count:
                max_count = count
                max_delimiter = delimiter
        except:
            continue

    return max_delimiter