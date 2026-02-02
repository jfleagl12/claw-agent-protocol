#!/usr/bin/env python3
"""
CAP Query Builder

Generates CAP query strings from natural language descriptions.

Usage:
    python build_query.py "<natural_language_query>"
    
Examples:
    python build_query.py "show me high priority tasks due this week"
    python build_query.py "unread emails from john@example.com"
    python build_query.py "calendar events for next month"
"""

import sys
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class QueryBuilder:
    """Build CAP queries from natural language"""
    
    # Shelf detection patterns
    SHELF_PATTERNS = {
        "calendar": ["calendar", "event", "meeting", "appointment", "schedule"],
        "tasks": ["task", "todo", "project", "milestone", "deadline"],
        "comms": ["email", "message", "communication", "call", "conversation"],
        "identity": ["contact", "person", "people", "organization", "client"],
        "docs": ["document", "note", "file", "bookmark", "snippet"]
    }
    
    # Time patterns
    TIME_PATTERNS = {
        "today": ("today", "today"),
        "tomorrow": ("+1days", "+1days"),
        "yesterday": ("-1days", "-1days"),
        "this week": ("today", "+7days"),
        "next week": ("+7days", "+14days"),
        "last week": ("-7days", "today"),
        "this month": ("today", "+30days"),
        "next month": ("+30days", "+60days"),
        "last month": ("-30days", "today"),
    }
    
    # Priority patterns
    PRIORITY_PATTERNS = {
        "urgent": "urgent",
        "high priority": "high",
        "high": "high",
        "medium priority": "medium",
        "medium": "medium",
        "low priority": "low",
        "low": "low"
    }
    
    # Status patterns
    STATUS_PATTERNS = {
        "pending": "pending",
        "active": "active",
        "blocked": "blocked",
        "completed": "completed",
        "cancelled": "cancelled",
        "done": "completed",
        "in progress": "active"
    }
    
    def __init__(self, query: str):
        self.query = query.lower()
        self.shelf = None
        self.filters = {}
    
    def build(self) -> str:
        """Build the CAP query string"""
        # Detect shelf
        self.shelf = self._detect_shelf()
        
        if not self.shelf:
            return f"# Error: Could not determine shelf from query: '{self.query}'"
        
        # Extract filters
        self._extract_time_filters()
        self._extract_priority_filters()
        self._extract_status_filters()
        self._extract_read_filters()
        self._extract_type_filters()
        self._extract_email_filters()
        self._extract_tag_filters()
        
        # Build query string
        query_str = f"cap://{self.shelf}"
        
        if self.filters:
            params = "&".join([f"{k}={v}" for k, v in self.filters.items()])
            query_str += f"?{params}"
        
        return query_str
    
    def _detect_shelf(self) -> str:
        """Detect which shelf to query"""
        for shelf, keywords in self.SHELF_PATTERNS.items():
            for keyword in keywords:
                if keyword in self.query:
                    return shelf
        return None
    
    def _extract_time_filters(self):
        """Extract time-based filters"""
        for pattern, (start, end) in self.TIME_PATTERNS.items():
            if pattern in self.query:
                if self.shelf == "calendar":
                    self.filters["start_date"] = start
                    self.filters["end_date"] = end
                elif self.shelf == "tasks":
                    self.filters["due_date_start"] = start
                    self.filters["due_date_end"] = end
                elif self.shelf == "comms":
                    self.filters["timestamp_after"] = start
                    if end != start:
                        self.filters["timestamp_before"] = end
                return
        
        # Check for "due" keyword
        if "due" in self.query and self.shelf == "tasks":
            if "today" in self.query:
                self.filters["due_date"] = "today"
            elif "tomorrow" in self.query:
                self.filters["due_date"] = "+1days"
    
    def _extract_priority_filters(self):
        """Extract priority filters"""
        if self.shelf != "tasks":
            return
        
        for pattern, priority in self.PRIORITY_PATTERNS.items():
            if pattern in self.query:
                self.filters["priority"] = priority
                return
    
    def _extract_status_filters(self):
        """Extract status filters"""
        if self.shelf not in ["tasks", "calendar"]:
            return
        
        for pattern, status in self.STATUS_PATTERNS.items():
            if pattern in self.query:
                self.filters["status"] = status
                return
    
    def _extract_read_filters(self):
        """Extract read/unread filters"""
        if self.shelf != "comms":
            return
        
        if "unread" in self.query:
            self.filters["is_read"] = "false"
        elif "read" in self.query:
            self.filters["is_read"] = "true"
    
    def _extract_type_filters(self):
        """Extract type filters"""
        type_map = {
            "calendar": {
                "event": "event",
                "reminder": "reminder",
                "block": "block"
            },
            "tasks": {
                "task": "task",
                "project": "project",
                "milestone": "milestone"
            },
            "comms": {
                "email": "email",
                "message": "message",
                "call": "call"
            },
            "identity": {
                "person": "person",
                "people": "person",
                "organization": "org",
                "org": "org",
                "role": "role"
            },
            "docs": {
                "note": "note",
                "file": "file",
                "snippet": "snippet",
                "bookmark": "bookmark"
            }
        }
        
        if self.shelf in type_map:
            for keyword, type_value in type_map[self.shelf].items():
                if keyword in self.query:
                    self.filters["type"] = type_value
                    return
    
    def _extract_email_filters(self):
        """Extract email address filters"""
        # Look for email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, self.query)
        
        if emails:
            email = emails[0]
            if self.shelf == "comms":
                if "from" in self.query:
                    self.filters["from"] = email
                elif "to" in self.query:
                    self.filters["to"] = email
                else:
                    # Default to from
                    self.filters["from"] = email
            elif self.shelf == "calendar":
                self.filters["attendee"] = email
    
    def _extract_tag_filters(self):
        """Extract tag filters"""
        # Look for "tagged" or "tag" keywords
        if "tagged" in self.query or "tag:" in self.query:
            # Extract tag name (word after "tagged" or "tag:")
            match = re.search(r'(?:tagged|tag:)\s+(\w+)', self.query)
            if match:
                self.filters["tags"] = match.group(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python build_query.py \"<natural_language_query>\"", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print('  python build_query.py "show me high priority tasks due this week"', file=sys.stderr)
        print('  python build_query.py "unread emails from john@example.com"', file=sys.stderr)
        print('  python build_query.py "calendar events for next month"', file=sys.stderr)
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    builder = QueryBuilder(query)
    result = builder.build()
    
    print(result)
    
    # Also print explanation
    if result.startswith("cap://"):
        print(f"\n# Query Explanation:")
        print(f"# Shelf: {builder.shelf}")
        if builder.filters:
            print(f"# Filters:")
            for key, value in builder.filters.items():
                print(f"#   - {key}: {value}")
        else:
            print(f"# No filters applied")

if __name__ == "__main__":
    main()
