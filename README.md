# Claw Agent Protocol (CAP) Skill

> **A production-grade skill for AI agents to interact with personal data through the Claw Agent Protocol.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/jfleagl12/claw-agent-protocol)

## Overview

The **Claw Agent Protocol (CAP) Skill** enables any AI agent to interact with a user's personal data in a structured, secure, and efficient manner. This skill provides a comprehensive framework for organizing, querying, and managing personal data across multiple sources.

### What is CAP?

CAP is a lightweight **Model Context Protocol (MCP) server** that acts as a real-time translation layer between a user's data sources (Gmail, Google Calendar, Notion, Slack, etc.) and AI agents. Instead of dealing with dozens of different APIs and data formats, agents can use a single, consistent interface.

### Why This Skill?

This skill transforms a general-purpose AI agent into a specialized personal data assistant by providing:

- **Canonical Schema**: Consistent data structures across all sources
- **Query Patterns**: Pre-built query examples for common use cases
- **Security Guidelines**: Best practices for handling sensitive data
- **Utility Scripts**: Production-ready tools for data validation, export, and query building
- **30+ Use Cases**: Real-world scenarios demonstrating CAP's capabilities

## Features

### 📚 Comprehensive Documentation

- **SKILL.md**: Main entry point with core concepts and usage instructions
- **Schema Reference**: Complete canonical schema for all 5 shelves (Identity, Comms, Calendar, Docs, Tasks)
- **Query Examples**: 50+ query patterns with filters and parameters
- **Security Guide**: Data sensitivity tiers, permissions, and safe handling practices
- **Use Cases**: 30 common scenarios from daily briefings to project management

### 🛠️ Production-Ready Utilities

1. **`generate_briefing.py`**: Format CAP data into readable daily briefings
2. **`validate_cap_data.py`**: Validate data against canonical schema requirements
3. **`export_cap_data.py`**: Export data to CSV, JSON, or Markdown formats
4. **`build_query.py`**: Generate CAP queries from natural language

### 🔒 Security-First Design

- Sensitivity tier classification (S1, S2, S3)
- Permission scoping and time-bounded grants
- Human-in-the-loop gates for sensitive operations
- Audit logging and data provenance tracking

## Installation

### For Manus AI Users

1. Download the `.skill` file from the releases page
2. In Manus, go to Settings → Skills
3. Click "Add Skill" and select the downloaded file
4. The skill will be automatically available for use

### For Other AI Agents like Clawdbot, Moltbot, OpenClaw:

1. Clone this repository or download the skill directory or copy and paste this repo link to your Openclaw ai agent and tell them to add the skill
2. Place the `claw-agent-protocol` directory in your agent's skills folder
3. Ensure your agent can read the `SKILL.md` file and execute Python scripts

## Quick Start

Once you've installed the skill and connected your CAP server, you can start using these prompts with your OpenClaw agent. Simply copy and paste these commands—no coding required.

### Example 1: Get Your Daily Briefing

**Copy this prompt:**
```
Give me my daily briefing using CAP
```

**What happens:** Your agent will fetch today's calendar events, due tasks, and recent communications, then format them into a readable summary.

---

### Example 2: Find High-Priority Tasks Due This Week

**Copy this prompt:**
```
Show me all high-priority tasks due this week from my CAP data
```

**What happens:** Your agent will query your tasks shelf and return all pending high-priority items with due dates in the next 7 days.

---

### Example 3: Check Unread Emails from a Specific Person

**Copy this prompt:**
```
Show me unread emails from john@example.com using CAP
```

**What happens:** Your agent will query your communications shelf and return all unread emails from that sender.

---

### Example 4: Get This Week's Calendar Events

**Copy this prompt:**
```
What's on my calendar this week? Use CAP to get the events
```

**What happens:** Your agent will fetch all confirmed calendar events for the next 7 days.

---

### Example 5: Find All Notes Tagged with a Specific Topic

**Copy this prompt:**
```
Find all my notes tagged with "project-alpha" using CAP
```

**What happens:** Your agent will search your docs shelf for notes with that tag.

---

### Example 6: Get Client Communication History

**Copy this prompt:**
```
Show me all communications with Acme Corp from the last 30 days using CAP
```

**What happens:** Your agent will query both your identity shelf (to find Acme Corp contacts) and comms shelf (to get recent messages/emails).

---

### Example 7: List All Blocked Tasks

**Copy this prompt:**
```
What tasks are currently blocked? Check CAP
```

**What happens:** Your agent will query your tasks shelf for items with status="blocked" and show you what's stuck.

---

### Example 8: Find Meetings with a Specific Person This Month

**Copy this prompt:**
```
Show me all meetings with sarah@example.com this month from CAP
```

**What happens:** Your agent will query your calendar shelf filtered by attendee email.

---

### Example 9: Get All VIP Contacts

**Copy this prompt:**
```
Show me all contacts tagged as VIP in CAP
```

**What happens:** Your agent will query your identity shelf for people/orgs with the "vip" tag.

---

### Example 10: Search Across All Documents

**Copy this prompt:**
```
Search my CAP documents for anything related to "quarterly budget"
```

**What happens:** Your agent will use the knowledge_search tool to find all docs, notes, and files mentioning that topic.

---

### Example 11: Weekly Planning Session

**Copy this prompt:**
```
Help me plan next week. Show me my calendar, pending tasks, and any upcoming deadlines from CAP
```

**What happens:** Your agent will aggregate data from multiple shelves (calendar, tasks) to give you a comprehensive weekly overview.

---

### Example 12: Export Your Tasks to a File

**Copy this prompt:**
```
Export all my pending tasks from CAP to a markdown file
```

**What happens:** Your agent will query your tasks shelf and use the export script to create a formatted markdown file you can download.

---

## Pro Tips

- **Be specific about time ranges**: "this week", "next month", "last 30 days"
- **Mention CAP explicitly**: This helps your agent know to use this skill
- **Combine shelves**: Ask for cross-referenced data like "meetings and related emails"
- **Use tags**: If you tag your data, you can filter by tags in your prompts
- **Ask for exports**: Your agent can export data to CSV, JSON, or Markdown formats

## Architecture

```
claw-agent-protocol/
├── SKILL.md                    # Main skill instructions (104 lines)
├── LICENSE                     # MIT License
├── README.md                   # This file
├── references/
│   ├── schema.md              # Canonical schema definitions (118 lines)
│   ├── query_examples.md      # Query patterns and filters (232 lines)
│   ├── security.md            # Security best practices (297 lines)
│   └── use_cases.md           # 30 common scenarios (466 lines)
└── scripts/
    ├── generate_briefing.py   # Daily briefing formatter (48 lines)
    ├── validate_cap_data.py   # Schema validator (299 lines)
    ├── export_cap_data.py     # Data exporter (306 lines)
    └── build_query.py         # Natural language query builder (255 lines)
```

**Total**: 2,146 lines of production-grade code and documentation

## CAP Shelves

CAP organizes personal data into 5 canonical shelves:

| Shelf | URI | Description |
|-------|-----|-------------|
| **Identity** | `cap://identity` | People, organizations, contacts |
| **Comms** | `cap://comms` | Messages, emails, threads |
| **Calendar** | `cap://calendar` | Events, availability, meetings |
| **Docs** | `cap://docs` | Notes, files, snippets, bookmarks |
| **Tasks** | `cap://tasks` | Tasks, projects, milestones |

Each shelf has a consistent schema with common metadata (id, timestamps, source, confidence, sensitivity).

## Use Cases

This skill supports 30+ common use cases, including:

### Personal Productivity
- Daily briefing generation
- Weekly planning assistance
- Task prioritization
- Meeting preparation
- Email triage

### Client & Relationship Management
- Client communication history
- Follow-up reminders
- Relationship strength analysis
- Meeting scheduling optimization
- Deliverable tracking

### Knowledge Management
- Cross-reference search
- Meeting notes consolidation
- Document version tracking
- Research thread reconstruction
- Knowledge gap identification

### Time & Availability
- Time audits
- Focus time protection
- Availability sharing
- Overcommitment detection
- Travel planning integration

### Project & Team Coordination
- Project status dashboards
- Dependency mapping
- Team workload balancing
- Milestone tracking
- Standup report generation

### Personal Life Management
- Family calendar coordination
- Health appointment tracking
- Financial deadline management
- Personal goal tracking
- Digital life audit

## Security & Privacy

This skill implements security best practices:

- **Data Sensitivity Tiers**: S1 (public), S2 (internal), S3 (sensitive)
- **Permission Scoping**: Read/write permissions per shelf
- **Time-Bounded Grants**: Temporary access for sensitive operations
- **Human-in-the-Loop**: Confirmation required for destructive actions
- **Audit Logging**: Append-only logs for critical operations
- **Data Provenance**: Full traceability to source systems

## Requirements

- Python 3.10+
- Access to a CAP MCP server
- MCP-compatible AI agent (OpenClaw, Claude Desktop, etc.)

## Contributing

Contributions are welcome! This skill is designed to be extended and improved by the community.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas for Contribution

- Additional utility scripts
- More use case examples
- Connector implementations for new data sources
- Improved query patterns
- Enhanced security features
- Documentation improvements

## License

This skill is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Author

**Jason Fleagle** - Chief AI Officer

CAP is created by Jason Fleagle. Jason is a Chief AI Officer and Growth Consultant working with global brands to help with their successful AI adoption and management. He is also a writer, entrepreneur, and consultant specializing in tech, marketing, and growth. He helps humanize data—so every growth decision an organization makes is rooted in clarity and confidence. Jason has helped lead the development and delivery of over 500 AI projects & tools, and frequently conducts training workshops to help companies understand and adopt AI. With a strong background in digital marketing, content strategy, and technology, he combines technical expertise with business acumen to create scalable solutions. He is also a content creator, producing videos, workshops, and thought leadership on AI, entrepreneurship, and growth. He continues to explore ways to leverage AI for good and improve human-to-human connections while balancing family, business, and creative pursuits.

## Acknowledgments
- Inspired by the Model Context Protocol (MCP) standard


---

**Built with ❤️ by a senior software engineer & AI Architect for the AI agent community.**
