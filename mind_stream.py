# mind_stream.py
import re
import time
from typing import Generator

def parse_line(line: str) -> dict:
    """
    Extracts tagged content and returns structured dict.
    """
    match = re.match(r"\[(\w+)] (.+)", line.strip())
    if match:
        return {
            "type": match.group(1),
            "content": match.group(2)
        }
    return {
        "type": "UNKNOWN",
        "content": line.strip()
    }

def stream_log_file(path: str) -> Generator[dict, None, None]:
    """
    Streams new lines from a log file and yields parsed output.
    """
    with open(path, 'r', encoding='utf-8') as f:
        f.seek(0, 2)  # Start at end of file
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield parse_line(line)
