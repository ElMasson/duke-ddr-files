def get_file_stats(file):
    """
    Get basic statistics about a file
    Args:
        file: The uploaded file object from Streamlit
    Returns:
        dict: Basic statistics about the file
    """
    stats = {
        'name': file.name,
        'type': file.type,
        'size': file.size,  # Size in bytes
    }

    # Convert size to human-readable format
    stats['size_human'] = convert_size(stats['size'])

    return stats


def convert_size(size_bytes):
    """
    Convert size in bytes to a human-readable format
    Args:
        size_bytes: Size in bytes
    Returns:
        str: Human-readable size
    """
    import math
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"