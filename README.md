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

### Example 1: Daily Briefing

```python
# Agent executes the today_briefing tool
tools.today_briefing()

# Returns: Calendar events, due tasks, and recent communications for today
```

### Example 2: Query High-Priority Tasks

```python
# Agent constructs a query
query = "cap://tasks?status=pending&priority=high&due_date_end=+7days"

# Or uses the query builder
python scripts/build_query.py "show me high priority tasks due this week"
# Output: cap://tasks?due_date_start=today&due_date_end=+7days&priority=high&type=task
```

### Example 3: Validate Data

```python
# Validate a task object
python scripts/validate_cap_data.py '{"id": "task-123", "type": "task", ...}' tasks
# Output: ✅ VALIDATION PASSED
```

### Example 4: Export Calendar Events

```python
# Export calendar data to Markdown
python scripts/export_cap_data.py --format markdown --shelf calendar --output events.md --data '[...]'
# Output: ✅ Exported 15 items to events.md
```

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

## Links

- [CAP GitHub Repository](https://github.com/jfleagl12/claw-agent-protocol)
- [CAP Whitepaper](https://github.com/jfleagl12/claw-agent-protocol/blob/main/docs/whitepaper.md)
- [Manus Skills Documentation](https://manus.im/docs/en/features/skills)

---

**Built with ❤️ by a senior software engineer & AI Architect for the AI agent community.**
