#!/usr/bin/env python3
"""
CAP Data Validator

Validates CAP data objects against the canonical schema requirements.
Checks for required fields, data types, and value constraints.

Usage:
    python validate_cap_data.py '<json_data>'
    
Example:
    python validate_cap_data.py '{"id": "123", "type": "task", "title": "Test", "status": "pending", "priority": "high"}'
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class CAPValidator:
    """Validator for CAP data objects"""
    
    # Valid values for enum fields
    VALID_IDENTITY_TYPES = ["person", "org", "role"]
    VALID_COMMS_TYPES = ["email", "message", "call"]
    VALID_CALENDAR_TYPES = ["event", "reminder", "block"]
    VALID_CALENDAR_STATUSES = ["confirmed", "tentative", "cancelled"]
    VALID_ATTENDEE_STATUSES = ["accepted", "declined", "tentative", "pending"]
    VALID_DOCS_TYPES = ["note", "file", "snippet", "bookmark"]
    VALID_TASK_TYPES = ["task", "project", "milestone"]
    VALID_TASK_STATUSES = ["pending", "active", "blocked", "completed", "cancelled"]
    VALID_TASK_PRIORITIES = ["low", "medium", "high", "urgent"]
    VALID_SENSITIVITY_TIERS = ["S1", "S2", "S3"]
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, data: Dict[str, Any], shelf: Optional[str] = None) -> bool:
        """
        Validate a CAP data object
        
        Args:
            data: The data object to validate
            shelf: Optional shelf name (identity, comms, calendar, docs, tasks)
        
        Returns:
            True if valid, False otherwise
        """
        self.errors = []
        self.warnings = []
        
        try:
            # Validate common metadata
            self._validate_common_metadata(data)
            
            # Validate shelf-specific schema
            if shelf:
                shelf_validator = getattr(self, f"_validate_{shelf}", None)
                if shelf_validator:
                    shelf_validator(data)
                else:
                    self.warnings.append(f"No validator for shelf: {shelf}")
            else:
                # Try to infer shelf from data structure
                self._infer_and_validate_shelf(data)
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"Validation exception: {str(e)}")
            return False
    
    def _validate_common_metadata(self, data: Dict[str, Any]):
        """Validate common metadata fields present in all CAP objects"""
        
        # Required fields
        required = ["id", "created_at", "updated_at", "source", "confidence", "sensitivity"]
        for field in required:
            if field not in data:
                self.errors.append(f"Missing required field: {field}")
        
        # Validate field types and values
        if "id" in data and not isinstance(data["id"], str):
            self.errors.append(f"Field 'id' must be a string, got {type(data['id']).__name__}")
        
        if "created_at" in data:
            self._validate_iso8601(data["created_at"], "created_at")
        
        if "updated_at" in data:
            self._validate_iso8601(data["updated_at"], "updated_at")
        
        if "source" in data:
            self._validate_source_pointer(data["source"])
        
        if "confidence" in data:
            if not isinstance(data["confidence"], (int, float)):
                self.errors.append(f"Field 'confidence' must be a number, got {type(data['confidence']).__name__}")
            elif not (0.0 <= data["confidence"] <= 1.0):
                self.errors.append(f"Field 'confidence' must be between 0.0 and 1.0, got {data['confidence']}")
        
        if "sensitivity" in data:
            if data["sensitivity"] not in self.VALID_SENSITIVITY_TIERS:
                self.errors.append(f"Invalid sensitivity tier: {data['sensitivity']}. Valid values: {', '.join(self.VALID_SENSITIVITY_TIERS)}")
    
    def _validate_source_pointer(self, source: Any):
        """Validate SourcePointer object"""
        if not isinstance(source, dict):
            self.errors.append(f"Field 'source' must be an object, got {type(source).__name__}")
            return
        
        required = ["system", "external_id"]
        for field in required:
            if field not in source:
                self.errors.append(f"Missing required field in source: {field}")
        
        if "url" in source and source["url"] and not isinstance(source["url"], str):
            self.errors.append(f"Field 'source.url' must be a string or null")
    
    def _validate_iso8601(self, value: Any, field_name: str):
        """Validate ISO8601 timestamp"""
        if not isinstance(value, str):
            self.errors.append(f"Field '{field_name}' must be an ISO8601 string, got {type(value).__name__}")
            return
        
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            self.errors.append(f"Field '{field_name}' is not a valid ISO8601 timestamp: {value}")
    
    def _infer_and_validate_shelf(self, data: Dict[str, Any]):
        """Infer shelf type from data structure and validate"""
        if "name" in data and "emails" in data:
            self._validate_identity(data)
        elif "thread_id" in data and "from" in data:
            self._validate_comms(data)
        elif "start_time" in data and "end_time" in data:
            self._validate_calendar(data)
        elif "content_preview" in data or "url" in data:
            self._validate_docs(data)
        elif "status" in data and "priority" in data:
            self._validate_tasks(data)
        else:
            self.warnings.append("Could not infer shelf type from data structure")
    
    def _validate_identity(self, data: Dict[str, Any]):
        """Validate Identity shelf data"""
        if "type" in data and data["type"] not in self.VALID_IDENTITY_TYPES:
            self.errors.append(f"Invalid identity type: {data['type']}. Valid values: {', '.join(self.VALID_IDENTITY_TYPES)}")
        
        if "name" in data:
            if not isinstance(data["name"], dict):
                self.errors.append("Field 'name' must be an object")
            else:
                if "full" not in data["name"]:
                    self.warnings.append("Missing recommended field: name.full")
                if "display" not in data["name"]:
                    self.warnings.append("Missing recommended field: name.display")
        
        if "emails" in data and not isinstance(data["emails"], list):
            self.errors.append("Field 'emails' must be an array")
        
        if "phones" in data and not isinstance(data["phones"], list):
            self.errors.append("Field 'phones' must be an array")
        
        if "tags" in data and not isinstance(data["tags"], list):
            self.errors.append("Field 'tags' must be an array")
    
    def _validate_comms(self, data: Dict[str, Any]):
        """Validate Comms shelf data"""
        if "type" in data and data["type"] not in self.VALID_COMMS_TYPES:
            self.errors.append(f"Invalid comms type: {data['type']}. Valid values: {', '.join(self.VALID_COMMS_TYPES)}")
        
        required = ["from", "to", "timestamp"]
        for field in required:
            if field not in data:
                self.errors.append(f"Missing required field: {field}")
        
        if "to" in data and not isinstance(data["to"], list):
            self.errors.append("Field 'to' must be an array")
        
        if "timestamp" in data:
            self._validate_iso8601(data["timestamp"], "timestamp")
        
        if "is_read" in data and not isinstance(data["is_read"], bool):
            self.errors.append("Field 'is_read' must be a boolean")
    
    def _validate_calendar(self, data: Dict[str, Any]):
        """Validate Calendar shelf data"""
        if "type" in data and data["type"] not in self.VALID_CALENDAR_TYPES:
            self.errors.append(f"Invalid calendar type: {data['type']}. Valid values: {', '.join(self.VALID_CALENDAR_TYPES)}")
        
        required = ["title", "start_time", "end_time"]
        for field in required:
            if field not in data:
                self.errors.append(f"Missing required field: {field}")
        
        if "start_time" in data:
            self._validate_iso8601(data["start_time"], "start_time")
        
        if "end_time" in data:
            self._validate_iso8601(data["end_time"], "end_time")
        
        if "all_day" in data and not isinstance(data["all_day"], bool):
            self.errors.append("Field 'all_day' must be a boolean")
        
        if "status" in data and data["status"] not in self.VALID_CALENDAR_STATUSES:
            self.errors.append(f"Invalid calendar status: {data['status']}. Valid values: {', '.join(self.VALID_CALENDAR_STATUSES)}")
        
        if "attendees" in data:
            if not isinstance(data["attendees"], list):
                self.errors.append("Field 'attendees' must be an array")
            else:
                for i, attendee in enumerate(data["attendees"]):
                    if not isinstance(attendee, dict):
                        self.errors.append(f"Attendee {i} must be an object")
                        continue
                    if "email" not in attendee:
                        self.errors.append(f"Attendee {i} missing required field: email")
                    if "status" in attendee and attendee["status"] not in self.VALID_ATTENDEE_STATUSES:
                        self.errors.append(f"Invalid attendee status: {attendee['status']}")
    
    def _validate_docs(self, data: Dict[str, Any]):
        """Validate Docs shelf data"""
        if "type" in data and data["type"] not in self.VALID_DOCS_TYPES:
            self.errors.append(f"Invalid docs type: {data['type']}. Valid values: {', '.join(self.VALID_DOCS_TYPES)}")
        
        if "title" not in data:
            self.errors.append("Missing required field: title")
        
        if "tags" in data and not isinstance(data["tags"], list):
            self.errors.append("Field 'tags' must be an array")
    
    def _validate_tasks(self, data: Dict[str, Any]):
        """Validate Tasks shelf data"""
        if "type" in data and data["type"] not in self.VALID_TASK_TYPES:
            self.errors.append(f"Invalid task type: {data['type']}. Valid values: {', '.join(self.VALID_TASK_TYPES)}")
        
        required = ["title", "status", "priority"]
        for field in required:
            if field not in data:
                self.errors.append(f"Missing required field: {field}")
        
        if "status" in data and data["status"] not in self.VALID_TASK_STATUSES:
            self.errors.append(f"Invalid task status: {data['status']}. Valid values: {', '.join(self.VALID_TASK_STATUSES)}")
        
        if "priority" in data and data["priority"] not in self.VALID_TASK_PRIORITIES:
            self.errors.append(f"Invalid task priority: {data['priority']}. Valid values: {', '.join(self.VALID_TASK_PRIORITIES)}")
        
        if "due_date" in data and data["due_date"] is not None:
            self._validate_iso8601(data["due_date"], "due_date")
    
    def get_report(self) -> str:
        """Generate a validation report"""
        report = []
        
        if self.errors:
            report.append("❌ VALIDATION FAILED\n")
            report.append("Errors:")
            for error in self.errors:
                report.append(f"  - {error}")
        else:
            report.append("✅ VALIDATION PASSED")
        
        if self.warnings:
            report.append("\nWarnings:")
            for warning in self.warnings:
                report.append(f"  - {warning}")
        
        return "\n".join(report)

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_cap_data.py '<json_data>' [shelf]", file=sys.stderr)
        print("\nExample:")
        print('  python validate_cap_data.py \'{"id": "123", "type": "task", ...}\' tasks', file=sys.stderr)
        sys.exit(1)
    
    try:
        data = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON data provided.\n{str(e)}", file=sys.stderr)
        sys.exit(1)
    
    shelf = sys.argv[2] if len(sys.argv) > 2 else None
    
    validator = CAPValidator()
    is_valid = validator.validate(data, shelf)
    
    print(validator.get_report())
    
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
