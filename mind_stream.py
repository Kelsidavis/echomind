import time
import re
from typing import Generator

def parse_line(line: str) -> dict:
    """
    Extracts tagged content and returns structured dict.
    Supports [TAG] content and [timestamp] as valid types.
    """
    line = line.strip()
    if not line:
        return None  # Skip blank lines

    # Match [TAG] content
    match = re.match(r"\[(\w+)] (.+)", line)
    if match:
        return {
            "type": match.group(1),
            "content": match.group(2)
        }

    # Match timestamp-only lines like: [2025-05-20 16:44:28]
    timestamp_match = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})]$", line)
    if timestamp_match:
        return {
            "type": "TIMESTAMP",
            "content": timestamp_match.group(1)
        }

    return {
        "type": "UNKNOWN",
        "content": line
    }

def stream_log_file(path: str) -> Generator[dict, None, None]:
    """
    Continuously reads from a log file and yields structured entries.
    """
    with open(path, 'r', encoding='utf-8') as f:
        f.seek(0, 2)  # Start at end of file
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            parsed = parse_line(line)
            if parsed:
                yield parsed
