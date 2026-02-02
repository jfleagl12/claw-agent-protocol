import json
import sys
from datetime import datetime

def format_event(event):
    start_time = datetime.fromisoformat(event["start_time"]).strftime("%I:%M %p")
    return f"- **{event['title']}** at {start_time}"

def format_task(task):
    return f"- **{task['title']}** (Priority: {task['priority']})"

def format_comm(comm):
    return f"- **{comm['subject']}** from {comm['from']}"

def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_briefing.py <json_data>", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print("Error: Invalid JSON data provided.", file=sys.stderr)
        sys.exit(1)

    output = "# Your Daily Briefing\n\n"

    if data.get("calendar_events"):
        output += "## Today's Events\n"
        for event in data["calendar_events"]:
            output += format_event(event) + "\n"
        output += "\n"

    if data.get("due_tasks"):
        output += "## Due Tasks\n"
        for task in data["due_tasks"]:
            output += format_task(task) + "\n"
        output += "\n"

    if data.get("recent_comms"):
        output += "## Recent Communications\n"
        for comm in data["recent_comms"]:
            output += format_comm(comm) + "\n"

    print(output)

if __name__ == "__main__":
    main()
