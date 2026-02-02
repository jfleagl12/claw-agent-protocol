#!/usr/bin/env python3
"""
CAP Data Exporter

Exports CAP data to various formats (CSV, JSON, Markdown).

Usage:
    python export_cap_data.py --format <format> --shelf <shelf> --output <file> [--data <json>]
    
Examples:
    python export_cap_data.py --format csv --shelf tasks --output tasks.csv --data '[{...}]'
    python export_cap_data.py --format markdown --shelf calendar --output events.md --data '[{...}]'
"""

import json
import sys
import csv
import argparse
from datetime import datetime
from typing import List, Dict, Any

class CAPExporter:
    """Exporter for CAP data to various formats"""
    
    def __init__(self, data: List[Dict[str, Any]], shelf: str):
        self.data = data
        self.shelf = shelf
    
    def export_csv(self, output_file: str):
        """Export data to CSV format"""
        if not self.data:
            print("Warning: No data to export", file=sys.stderr)
            return
        
        # Determine fields based on shelf type
        fields = self._get_csv_fields()
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            
            for item in self.data:
                # Flatten nested structures for CSV
                flat_item = self._flatten_item(item)
                writer.writerow(flat_item)
        
        print(f"✅ Exported {len(self.data)} items to {output_file}")
    
    def export_json(self, output_file: str):
        """Export data to JSON format"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "shelf": self.shelf,
                "exported_at": datetime.utcnow().isoformat() + "Z",
                "count": len(self.data),
                "items": self.data
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported {len(self.data)} items to {output_file}")
    
    def export_markdown(self, output_file: str):
        """Export data to Markdown format"""
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# {self.shelf.title()} Export\n\n")
            f.write(f"**Exported:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write(f"**Total Items:** {len(self.data)}\n\n")
            f.write("---\n\n")
            
            # Write items based on shelf type
            if self.shelf == "calendar":
                self._export_calendar_markdown(f)
            elif self.shelf == "tasks":
                self._export_tasks_markdown(f)
            elif self.shelf == "comms":
                self._export_comms_markdown(f)
            elif self.shelf == "identity":
                self._export_identity_markdown(f)
            elif self.shelf == "docs":
                self._export_docs_markdown(f)
            else:
                self._export_generic_markdown(f)
        
        print(f"✅ Exported {len(self.data)} items to {output_file}")
    
    def _get_csv_fields(self) -> List[str]:
        """Get CSV field names based on shelf type"""
        common = ["id", "created_at", "updated_at", "source_system", "confidence", "sensitivity"]
        
        shelf_fields = {
            "calendar": ["type", "title", "start_time", "end_time", "all_day", "location", "status"],
            "tasks": ["type", "title", "status", "priority", "due_date", "project"],
            "comms": ["type", "thread_id", "from", "to", "subject", "timestamp", "is_read"],
            "identity": ["type", "name_full", "name_display", "emails", "phones", "tags"],
            "docs": ["type", "title", "content_preview", "url", "tags"]
        }
        
        return common + shelf_fields.get(self.shelf, [])
    
    def _flatten_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested structures for CSV export"""
        flat = {}
        
        # Copy simple fields
        for key in ["id", "type", "title", "status", "priority", "created_at", "updated_at", "confidence", "sensitivity"]:
            if key in item:
                flat[key] = item[key]
        
        # Flatten source
        if "source" in item and isinstance(item["source"], dict):
            flat["source_system"] = item["source"].get("system", "")
        
        # Flatten name (identity)
        if "name" in item and isinstance(item["name"], dict):
            flat["name_full"] = item["name"].get("full", "")
            flat["name_display"] = item["name"].get("display", "")
        
        # Convert arrays to comma-separated strings
        for key in ["emails", "phones", "tags", "to"]:
            if key in item and isinstance(item[key], list):
                flat[key] = ", ".join(str(x) for x in item[key])
        
        # Copy other fields
        for key in ["from", "subject", "timestamp", "is_read", "start_time", "end_time", 
                    "all_day", "location", "due_date", "project", "content_preview", "url", "thread_id"]:
            if key in item:
                flat[key] = item[key]
        
        return flat
    
    def _export_calendar_markdown(self, f):
        """Export calendar events to Markdown"""
        for item in self.data:
            f.write(f"## {item.get('title', 'Untitled Event')}\n\n")
            
            start = item.get('start_time', 'N/A')
            end = item.get('end_time', 'N/A')
            f.write(f"**When:** {start} - {end}\n\n")
            
            if item.get('location'):
                f.write(f"**Location:** {item['location']}\n\n")
            
            if item.get('attendees'):
                f.write("**Attendees:**\n")
                for attendee in item['attendees']:
                    status = attendee.get('status', 'pending')
                    f.write(f"- {attendee.get('email', 'Unknown')} ({status})\n")
                f.write("\n")
            
            f.write(f"**Status:** {item.get('status', 'unknown')}\n\n")
            f.write("---\n\n")
    
    def _export_tasks_markdown(self, f):
        """Export tasks to Markdown"""
        # Group by status
        by_status = {}
        for item in self.data:
            status = item.get('status', 'unknown')
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(item)
        
        for status, tasks in by_status.items():
            f.write(f"## {status.title()} Tasks\n\n")
            
            for task in tasks:
                priority = task.get('priority', 'medium')
                emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
                
                f.write(f"- {emoji} **{task.get('title', 'Untitled Task')}**")
                
                if task.get('due_date'):
                    f.write(f" (Due: {task['due_date']})")
                
                if task.get('project'):
                    f.write(f" - *{task['project']}*")
                
                f.write("\n")
            
            f.write("\n")
    
    def _export_comms_markdown(self, f):
        """Export communications to Markdown"""
        for item in self.data:
            comm_type = item.get('type', 'unknown')
            emoji = {"email": "📧", "message": "💬", "call": "📞"}.get(comm_type, "📄")
            
            f.write(f"## {emoji} {item.get('subject', 'No Subject')}\n\n")
            f.write(f"**From:** {item.get('from', 'Unknown')}\n\n")
            
            if item.get('to'):
                to_list = ", ".join(item['to']) if isinstance(item['to'], list) else item['to']
                f.write(f"**To:** {to_list}\n\n")
            
            f.write(f"**Time:** {item.get('timestamp', 'N/A')}\n\n")
            
            if item.get('body_preview'):
                f.write(f"**Preview:** {item['body_preview']}\n\n")
            
            f.write("---\n\n")
    
    def _export_identity_markdown(self, f):
        """Export identity/contacts to Markdown"""
        for item in self.data:
            name = item.get('name', {})
            display_name = name.get('display', name.get('full', 'Unknown'))
            
            f.write(f"## {display_name}\n\n")
            f.write(f"**Type:** {item.get('type', 'unknown')}\n\n")
            
            if item.get('emails'):
                f.write("**Emails:**\n")
                for email in item['emails']:
                    f.write(f"- {email}\n")
                f.write("\n")
            
            if item.get('phones'):
                f.write("**Phones:**\n")
                for phone in item['phones']:
                    f.write(f"- {phone}\n")
                f.write("\n")
            
            if item.get('tags'):
                tags = ", ".join(item['tags'])
                f.write(f"**Tags:** {tags}\n\n")
            
            f.write("---\n\n")
    
    def _export_docs_markdown(self, f):
        """Export documents to Markdown"""
        for item in self.data:
            f.write(f"## {item.get('title', 'Untitled Document')}\n\n")
            f.write(f"**Type:** {item.get('type', 'unknown')}\n\n")
            
            if item.get('url'):
                f.write(f"**URL:** [{item['url']}]({item['url']})\n\n")
            
            if item.get('content_preview'):
                f.write(f"**Preview:**\n\n{item['content_preview']}\n\n")
            
            if item.get('tags'):
                tags = ", ".join(item['tags'])
                f.write(f"**Tags:** {tags}\n\n")
            
            f.write("---\n\n")
    
    def _export_generic_markdown(self, f):
        """Export generic data to Markdown"""
        for item in self.data:
            f.write(f"## Item: {item.get('id', 'unknown')}\n\n")
            f.write("```json\n")
            f.write(json.dumps(item, indent=2))
            f.write("\n```\n\n")
            f.write("---\n\n")

def main():
    parser = argparse.ArgumentParser(description="Export CAP data to various formats")
    parser.add_argument("--format", required=True, choices=["csv", "json", "markdown", "md"],
                        help="Output format")
    parser.add_argument("--shelf", required=True, 
                        choices=["calendar", "tasks", "comms", "identity", "docs"],
                        help="CAP shelf type")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--data", help="JSON data to export (or read from stdin)")
    
    args = parser.parse_args()
    
    # Read data
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON data.\n{str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON from stdin.\n{str(e)}", file=sys.stderr)
            sys.exit(1)
    
    # Ensure data is a list
    if isinstance(data, dict) and "items" in data:
        data = data["items"]
    elif not isinstance(data, list):
        data = [data]
    
    # Export
    exporter = CAPExporter(data, args.shelf)
    
    format_map = {
        "csv": exporter.export_csv,
        "json": exporter.export_json,
        "markdown": exporter.export_markdown,
        "md": exporter.export_markdown
    }
    
    try:
        format_map[args.format](args.output)
    except Exception as e:
        print(f"❌ Export failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
