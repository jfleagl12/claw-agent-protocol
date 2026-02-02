# CAP Use Cases

This document outlines 30 common scenarios where AI agents can leverage CAP to organize and access personal data effectively.

## Personal Productivity

### 1. Daily Briefing Generation
**Scenario**: User wants a summary of their day every morning.

**CAP Usage**:
```
tools.today_briefing()
```

**Output**: Calendar events, due tasks, unread emails, and recent communications formatted as a daily briefing.

---

### 2. Weekly Planning Assistant
**Scenario**: User needs help planning their week ahead.

**CAP Usage**:
```
read cap://calendar?start_date=today&end_date=+7days
read cap://tasks?due_date_start=today&due_date_end=+7days&status=pending
```

**Output**: Week-at-a-glance view with events, deadlines, and available time blocks.

---

### 3. Task Prioritization
**Scenario**: User has too many tasks and needs help prioritizing.

**CAP Usage**:
```
read cap://tasks?status=pending
read cap://calendar?start_date=today&end_date=+3days
```

**Output**: Prioritized task list based on due dates, calendar availability, and task priority levels.

---

### 4. Meeting Preparation
**Scenario**: User has a meeting in 30 minutes and needs context.

**CAP Usage**:
```
read cap://calendar?start_date=now&end_date=+1hour
read cap://comms?from=<attendee_email>&timestamp_after=-30days
read cap://docs?tags=<meeting_topic>
```

**Output**: Meeting details, recent communications with attendees, and relevant documents.

---

### 5. Email Triage
**Scenario**: User has 200 unread emails and needs to identify urgent ones.

**CAP Usage**:
```
read cap://comms?type=email&is_read=false
read cap://identity?tags=vip,client
```

**Output**: Prioritized email list with VIP/client emails flagged, sorted by urgency indicators.

---

## Client and Relationship Management

### 6. Client Communication History
**Scenario**: User needs to review all interactions with a specific client.

**CAP Usage**:
```
tools.client_pipeline(client_name="Acme Corp")
```

**Output**: Complete communication timeline, tasks, meetings, and documents related to the client.

---

### 7. Follow-Up Reminders
**Scenario**: User wants to ensure they follow up with contacts who haven't responded.

**CAP Usage**:
```
read cap://comms?type=email&timestamp_after=-7days&from=<user>
read cap://comms?type=email&to=<user>&timestamp_after=-7days
```

**Output**: List of sent emails with no replies, suggesting follow-up actions.

---

### 8. Relationship Strength Analysis
**Scenario**: User wants to identify relationships that need nurturing.

**CAP Usage**:
```
read cap://identity?type=person
read cap://comms?timestamp_after=-90days
```

**Output**: Contact list with communication frequency analysis, highlighting neglected relationships.

---

### 9. Meeting Scheduling Optimization
**Scenario**: User needs to find the best time to schedule a meeting with multiple people.

**CAP Usage**:
```
read cap://calendar?start_date=today&end_date=+14days
read cap://identity?emails=<attendee_list>
```

**Output**: Available time slots that work for all attendees based on calendar availability.

---

### 10. Client Deliverable Tracking
**Scenario**: User needs to track deliverables and deadlines for multiple clients.

**CAP Usage**:
```
read cap://tasks?tags=client-deliverable&status=active,pending
read cap://calendar?type=event&tags=deadline
```

**Output**: Dashboard of client deliverables with status, deadlines, and progress indicators.

---

## Knowledge Management

### 11. Cross-Reference Search
**Scenario**: User remembers discussing a topic but can't recall where.

**CAP Usage**:
```
tools.knowledge_search(query="quarterly budget")
```

**Output**: All mentions across emails, notes, documents, and calendar events.

---

### 12. Meeting Notes Consolidation
**Scenario**: User wants to compile all meeting notes from a project.

**CAP Usage**:
```
read cap://docs?type=note&tags=project-alpha,meeting-notes
read cap://calendar?title_contains=Project Alpha&type=event
```

**Output**: Chronological compilation of all meeting notes with links to calendar events.

---

### 13. Document Version Tracking
**Scenario**: User needs to find the latest version of a document.

**CAP Usage**:
```
read cap://docs?title_contains=proposal&sort_by=updated_at&sort_order=desc
```

**Output**: Document list sorted by most recent update, with version history.

---

### 14. Research Thread Reconstruction
**Scenario**: User wants to reconstruct their research process on a topic.

**CAP Usage**:
```
read cap://docs?type=bookmark&tags=market-research
read cap://docs?type=note&tags=market-research
read cap://comms?subject_contains=market research
```

**Output**: Timeline of research activities including bookmarks, notes, and relevant emails.

---

### 15. Knowledge Gap Identification
**Scenario**: User wants to identify topics they haven't documented or learned about.

**CAP Usage**:
```
read cap://tasks?tags=learning,research
read cap://docs?type=note
```

**Output**: Analysis of documented knowledge vs. planned learning tasks, highlighting gaps.

---

## Time and Availability Management

### 16. Time Audit
**Scenario**: User wants to understand how they're spending their time.

**CAP Usage**:
```
read cap://calendar?start_date=-30days&end_date=today
```

**Output**: Time allocation breakdown by meeting type, project, and category.

---

### 17. Focus Time Protection
**Scenario**: User wants to identify and protect blocks of uninterrupted work time.

**CAP Usage**:
```
read cap://calendar?start_date=today&end_date=+7days
read cap://tasks?status=active&priority=high
```

**Output**: Recommended focus time blocks with automatic calendar blocking suggestions.

---

### 18. Availability Sharing
**Scenario**: User needs to share their availability with someone.

**CAP Usage**:
```
read cap://calendar?start_date=today&end_date=+14days&status=confirmed
```

**Output**: Formatted availability list excluding private/sensitive events.

---

### 19. Overcommitment Detection
**Scenario**: User wants to avoid scheduling conflicts and overcommitment.

**CAP Usage**:
```
read cap://calendar?start_date=today&end_date=+7days
read cap://tasks?due_date_end=+7days&status=pending
```

**Output**: Alert when calendar + task load exceeds sustainable capacity.

---

### 20. Travel Planning Integration
**Scenario**: User has upcoming travel and needs to coordinate schedule.

**CAP Usage**:
```
read cap://calendar?start_date=today&end_date=+90days&location_contains=<city>
read cap://tasks?tags=travel-prep
```

**Output**: Travel itinerary with pre-trip tasks, meetings scheduled during travel, and logistics.

---

## Project and Team Coordination

### 21. Project Status Dashboard
**Scenario**: User manages multiple projects and needs a status overview.

**CAP Usage**:
```
read cap://tasks?type=project
read cap://tasks?status=active,blocked
```

**Output**: Project dashboard with progress, blockers, and upcoming milestones.

---

### 22. Dependency Mapping
**Scenario**: User needs to understand task dependencies across projects.

**CAP Usage**:
```
read cap://tasks?status=blocked
read cap://tasks?status=active
```

**Output**: Dependency graph showing which tasks are blocking others.

---

### 23. Team Workload Balancing
**Scenario**: User wants to ensure team members aren't overloaded.

**CAP Usage**:
```
read cap://tasks?assigned_to=<team_member>&status=active,pending
read cap://calendar?attendee=<team_member>&start_date=today&end_date=+7days
```

**Output**: Team workload analysis with recommendations for task redistribution.

---

### 24. Milestone Tracking
**Scenario**: User needs to track progress toward project milestones.

**CAP Usage**:
```
read cap://tasks?type=milestone&project=<project_name>
read cap://tasks?project=<project_name>&status=completed
```

**Output**: Milestone completion percentage and projected completion dates.

---

### 25. Standup Report Generation
**Scenario**: User needs to prepare for daily standup meeting.

**CAP Usage**:
```
read cap://tasks?assigned_to=<user>&updated_after=-24hours
read cap://tasks?assigned_to=<user>&status=blocked
```

**Output**: Automated standup report: completed yesterday, planned today, blockers.

---

## Personal Life Management

### 26. Family Calendar Coordination
**Scenario**: User needs to coordinate personal and family schedules.

**CAP Usage**:
```
read cap://calendar?tags=family,personal&start_date=today&end_date=+7days
read cap://tasks?tags=household,errands&due_date_end=+7days
```

**Output**: Family calendar view with household tasks and personal commitments.

---

### 27. Health Appointment Tracking
**Scenario**: User wants to track medical appointments and health-related tasks.

**CAP Usage**:
```
read cap://calendar?tags=health,medical&start_date=today
read cap://docs?tags=medical-records
```

**Output**: Health appointment timeline with links to medical records and notes.

---

### 28. Financial Deadline Management
**Scenario**: User needs to track bill payments and financial deadlines.

**CAP Usage**:
```
read cap://tasks?tags=finance,bills&due_date_end=+30days
read cap://calendar?tags=payment-due
```

**Output**: Financial deadline calendar with payment reminders and amounts.

---

### 29. Personal Goal Tracking
**Scenario**: User wants to track progress on personal goals and habits.

**CAP Usage**:
```
read cap://tasks?tags=personal-goal&status=active,completed
read cap://docs?type=note&tags=journal,reflection
```

**Output**: Goal progress dashboard with completion rates and journal reflections.

---

### 30. Digital Life Audit
**Scenario**: User wants to understand their digital footprint and data organization.

**CAP Usage**:
```
read cap://identity
read cap://comms?timestamp_after=-90days
read cap://docs
read cap://tasks
read cap://calendar?start_date=-90days
```

**Output**: Comprehensive digital life report: communication patterns, document organization, time allocation, task completion rates, and relationship network analysis.

---

## Implementation Patterns

### Pattern 1: Data Aggregation
Combine multiple shelf queries to build comprehensive views:
```python
calendar = cap.read("cap://calendar?start_date=today")
tasks = cap.read("cap://tasks?due_date=today")
comms = cap.read("cap://comms?is_read=false")

briefing = aggregate_data(calendar, tasks, comms)
```

### Pattern 2: Contextual Filtering
Use identity data to filter other shelves:
```python
vip_contacts = cap.read("cap://identity?tags=vip")
vip_emails = [c["emails"][0] for c in vip_contacts]

urgent_comms = cap.read(f"cap://comms?from={','.join(vip_emails)}&is_read=false")
```

### Pattern 3: Temporal Analysis
Analyze data across time periods:
```python
last_week = cap.read("cap://comms?timestamp_after=-7days&timestamp_before=today")
this_week = cap.read("cap://comms?timestamp_after=today")

compare_communication_volume(last_week, this_week)
```

### Pattern 4: Cross-Shelf Correlation
Link data across multiple shelves:
```python
meeting = cap.read("cap://calendar?id=<event_id>")
attendees = meeting["attendees"]

for attendee in attendees:
    recent_comms = cap.read(f"cap://comms?from={attendee['email']}&timestamp_after=-30days")
    shared_docs = cap.read(f"cap://docs?shared_with={attendee['email']}")
```

### Pattern 5: Proactive Recommendations
Use data patterns to suggest actions:
```python
pending_tasks = cap.read("cap://tasks?status=pending&due_date_end=+3days")
calendar = cap.read("cap://calendar?start_date=today&end_date=+3days")

available_slots = find_gaps(calendar)
recommendations = match_tasks_to_slots(pending_tasks, available_slots)
```

## Best Practices for Use Case Implementation

1. **Start with views**: Use pre-built tools like `today_briefing` before building custom queries
2. **Cache intelligently**: Cache results for the duration of a task, but refresh for new requests
3. **Respect sensitivity**: Always check `sensitivity` field and handle S3 data appropriately
4. **Provide context**: Link back to source systems using the `source.url` field
5. **Handle errors gracefully**: Not all users will have all data sources connected
6. **Optimize queries**: Use filters to reduce data transfer and processing time
7. **Maintain provenance**: Always preserve the `source` field when transforming data
8. **User confirmation**: Ask before taking actions based on CAP data (sending emails, creating events)
