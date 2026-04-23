import os

def get_full_file_code(filename):
    """Opens the target file and returns the entire code string."""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    else:
        return None