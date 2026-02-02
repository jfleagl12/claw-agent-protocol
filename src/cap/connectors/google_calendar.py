"""
Google Calendar Connector

Fetches calendar events from Google Calendar API and normalizes to CAP schema.
"""

from typing import Any, Dict, List, Optional
import httpx
from datetime import datetime
from cap.connectors.base import CAPConnector


class GoogleCalendarConnector(CAPConnector):
    """Connector for Google Calendar API."""
    
    API_BASE = "https://www.googleapis.com/calendar/v3"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.access_token = config.get("access_token")
        self.calendar_id = config.get("calendar_id", "primary")
    
    async def authenticate(self) -> bool:
        """Authenticate with Google Calendar API."""
        if not self.access_token:
            raise ValueError("Google Calendar access token not configured")
        
        # Test the token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/users/me/calendarList",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 200:
                self._authenticated = True
                return True
            else:
                raise ValueError(f"Google Calendar auth failed: {response.text}")
    
    def get_supported_shelves(self) -> List[str]:
        """This connector supports the calendar shelf."""
        return ["calendar"]
    
    async def fetch_calendar(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch calendar events from Google Calendar.
        
        Args:
            start_date: ISO8601 date string
            end_date: ISO8601 date string
        
        Returns:
            List of normalized calendar events
        """
        if not self._authenticated:
            await self.authenticate()
        
        # Set defaults
        if not start_date or not end_date:
            start_date, end_date = self.get_default_date_range()
        
        # Convert to RFC3339 format for Google API
        time_min = f"{start_date}T00:00:00Z"
        time_max = f"{end_date}T23:59:59Z"
        
        # Fetch events
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/calendars/{self.calendar_id}/events",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={
                    "timeMin": time_min,
                    "timeMax": time_max,
                    "singleEvents": True,
                    "orderBy": "startTime"
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Google Calendar API error: {response.text}")
            
            data = response.json()
            events = data.get("items", [])
        
        # Normalize to CAP schema
        return [self._normalize_event(event) for event in events]
    
    def _normalize_event(self, raw_event: Dict) -> Dict:
        """
        Normalize a Google Calendar event to CAP schema.
        
        Args:
            raw_event: Raw event data from Google Calendar API
        
        Returns:
            Normalized CAP calendar object
        """
        # Extract start/end times
        start = raw_event.get("start", {})
        end = raw_event.get("end", {})
        
        start_time = start.get("dateTime") or start.get("date")
        end_time = end.get("dateTime") or end.get("date")
        all_day = "date" in start
        
        # Extract attendees
        attendees = []
        for attendee in raw_event.get("attendees", []):
            attendees.append({
                "email": attendee.get("email"),
                "status": attendee.get("responseStatus", "pending"),
                "organizer": attendee.get("organizer", False)
            })
        
        # Build normalized object
        return {
            "id": raw_event.get("id"),
            "type": "event",
            "title": raw_event.get("summary", "Untitled Event"),
            "description": raw_event.get("description"),
            "start_time": start_time,
            "end_time": end_time,
            "all_day": all_day,
            "location": raw_event.get("location"),
            "attendees": attendees,
            "recurrence": raw_event.get("recurrence"),
            "calendar_name": "Google Calendar",
            "status": raw_event.get("status", "confirmed"),
            "created_at": raw_event.get("created"),
            "updated_at": raw_event.get("updated"),
            "source": self.create_source_pointer(
                raw_event,
                raw_event.get("id"),
                raw_event.get("htmlLink")
            ),
            "confidence": 1.0,
            "sensitivity": "S1"
        }
