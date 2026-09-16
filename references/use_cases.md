# Supported workflows and future extensions

## Implemented in 0.2

**Daily briefing:** return today's overlapping calendar events and received mail in the user's timezone. The agent summarizes with source citations and explicit missing-coverage notes. Tasks are not part of this release.

**Meeting preparation:** select a specific event, retrieve recent same-account correspondence involving its exact attendee/organizer email addresses, and produce an evidence-based preparation brief. At most eight attendees are searched per call; omissions are reported. Related documents and inferred client relationships are not retrieved.

**Mail triage:** inspect unread mail within an explicit date window, optionally matching a participant or subject/preview substring. No source messages are changed or sent.

**Recurring follow-up review:** the harness schedules a bounded overlapping search; CAP returns unacknowledged revisions and stores successful handling only after explicit acknowledgement. Failed runs replay pending work.

**Connection diagnostics:** distinguish configured accounts from accounts that have passed live mail/calendar probes.

## Not yet implemented

Google Workspace, Notion, Slack, contacts/organization resolution, document search, task/project management, reminders, scheduling, financial or health record integrations, outbound messages, source writes, provider delta/deletion feeds, and multiple/shared calendars.

These remain extension candidates. Documentation does not create provider access or tools.
