def parse_logs(log_filepath):
    #parser.py
    with open(log_filepath, "r") as file:
        logs = file.readlines()

    errors = []
    current = ""
    temp = False

    for line in logs:
        if "ERROR:" in line or "Traceback" in line:
            if not temp:
                temp = True
                current = ""

        if temp and "INFO:" in line:
            temp = False
            errors.append(current)
            current = ""

        if temp:
            current += line

    if temp and current:
        errors.append(current)

    print(f"Found {len(errors)} errors in the log file.\n")

    for i, error in enumerate(errors):
        print(f"--- ERROR {i + 1} ---")
        print(error)

    print(f"Reading logs from: {log_filepath}")
    return errors
