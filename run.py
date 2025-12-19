import uvicorn
from constant import PATH_TO_LOG_FILE, PATH_TO_JSON_FILE
import uuid

def parse_log_line(line: str):
    
    print(f"Parsing line: {line.strip()}")
    parts = line.split("\\t")
    print(f"Split parts: {parts}")
    timestamp = parts[0].strip("[]")
    level = parts[1].strip("[]")
    component = parts[2].strip("[]").strip(":")
    message = parts[3].strip()
    return {
        "timestamp": timestamp,
        "level": level,
        "component": component,
        "message": message,
        "log_id": str(uuid.uuid4()),
    }


def parse_logs():
    logs = []
    with open(PATH_TO_LOG_FILE, "r") as f:
        for line in f:
            parsed = parse_log_line(line)
            if parsed:
                logs.append(parsed)
    return logs




def write_log_file_json():
    import json
    logs = parse_logs()
    sorted_logs = sorted(logs, key=lambda x: x["timestamp"])
    with open(PATH_TO_JSON_FILE, "w") as f:
        json.dump(sorted_logs, f, indent=4)


if __name__ == "__main__":
    write_log_file_json()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1)