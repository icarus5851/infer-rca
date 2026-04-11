import re
import os

def extract_location(error_text):
    """Parses the error text to find the filename and line number."""
    pattern = r'File "([^"]+)", line (\d+)'
    matches = re.findall(pattern, error_text)
    
    if matches:
        last_match = matches[-1]
        filename = last_match[0]
        line_number = int(last_match[1])
        return filename, line_number
        
    return None, None

def get_code_context(filename, line_number):
    """Opens the target file and extracts a 10-line context window."""
    if os.path.exists(filename):
        with open(filename, "r") as file:
            lines = file.readlines()

        error_index = line_number - 1
        start_index = max(0, error_index - 5)
        end_index = min(len(lines), error_index + 6) 

        context_lines = lines[start_index:end_index]
        return "".join(context_lines), start_index + 1
        
    else:
        return "File not found.", 1