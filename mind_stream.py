import time
import re
from typing import Generator

def parse_line(line: str) -> dict:
    """
    Extracts tagged content and returns structured dict.
    Supports [TAG] content, timestamps, and filters repeated noise.
    """
    line = line.strip()
    if not line:
        return None  # Skip blank lines

    # Skip LLM hallucinated prompt context or echo artifacts
    if line.startswith("You:") or line.startswith("EchoMind:") or line.startswith("Users say:"):
        return None
    if line.startswith("Q:") or "system state:" in line.lower():
        return None

    # Match [TAG] content
    match = re.match(r"\[(\w+)] (.+)", line)
    if match:
        return {
            "type": match.group(1).upper(),
            "content": match.group(2)
        }

    # Match standalone timestamps
    timestamp_match = re.match(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})]$", line)
    if timestamp_match:
        return {
            "type": "TIMESTAMP",
            "content": timestamp_match.group(1)
        }

    # Catch-all for non-tagged lines (only log if meaningful)
    if len(line) > 3:
        return {
            "type": "UNKNOWN",
            "content": line
        }

    return None


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
