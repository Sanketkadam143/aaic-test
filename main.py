import uuid
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
from constant import PATH_TO_JSON_FILE
import json
import run
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def calculate_log_stats(logs):
    global LOGS_STATS
    LOGS_STATS = {
        "levels": {
            "INFO": 0,
            "ERROR": 0,
            "DEBUG": 0,
        },
        "components": {
            "UserAuth": 0,
            "DataProcessing": 0,
            "API": 0,
        },
    }
    for log in logs:
        level = log["level"]
        component = log["component"]
        if level in LOGS_STATS["levels"]:
            LOGS_STATS["levels"][level] += 1
        if component in LOGS_STATS["components"]:
            LOGS_STATS["components"][component] += 1
    
    print(f"Calculated LOGS_STATS: {LOGS_STATS}")
    return LOGS_STATS


def parse_log_line(line: str):
    """
    Expected format:
    2025-05-07 10:00:12 | ERROR | UserAuth | Message
    """
    try:
        timestamp_str, level, component, message = map(str.strip, line.split("|", 3))
        return {
            "timestamp": datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S"),
            "level": level,
            "component": component,
            "message": message,
            "raw": line.strip(),
        }
    except Exception:
        return None


@app.get("/api/logs")
def read_logs(
    level: Optional[str] = Query(None, description="Filter by log level"),
    component: Optional[str] = Query(None, description="Filter by component"),
    start_time: Optional[str] = Query(None, description="YYYY-MM-DD HH:MM:SS"),
    end_time: Optional[str] = Query(None, description="YYYY-MM-DD HH:MM:SS"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
):
    with open(PATH_TO_JSON_FILE, "r") as f:
        lines = json.load(f)

    logs = []
    for line in lines:
        parsed = line
        if not parsed:
            continue

        if level and parsed["level"].lower() != level.lower():
            continue
        if component and parsed["component"].lower() != component.lower():
            continue

        if start_time:
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            if parsed["timestamp"] < start_dt:
                continue

        if end_time:
            end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            if parsed["timestamp"] > end_dt:
                continue

        logs.append(parsed)

    total = len(logs)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "logs": logs[start:end],
    }


@app.get("/api/logs/stats")
def log_stats():
    return calculate_log_stats(run.parse_logs())


@app.get("/api/logs/{log_id}")
def read_log(log_id: uuid.UUID):
    with open(PATH_TO_JSON_FILE, "r") as f:
        logs = json.load(f)

    for log in logs:
        if log.get("log_id") == str(log_id):
            return log
