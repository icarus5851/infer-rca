def get_log_tail(log_filepath, lines=200):
    with open(log_filepath, "r") as file:
        all_lines = file.readlines()
        tail_lines = all_lines[-lines:]
        return "".join(tail_lines)