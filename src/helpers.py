import os

def construct_csv_path(relative_path, csv_name):
    """
    Constructs a full path to a CSV file based on a relative path and the CSV file name.

    Args:
        relative_path: The relative path from the script's current directory to the directory containing the CSV.
        csv_name: The name of the CSV file.
    
    Returns:
        csv_path: The full path to the CSV file.
    """

    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, relative_path, csv_name)

    return csv_path
