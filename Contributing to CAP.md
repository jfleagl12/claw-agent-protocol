# Contributing to CAP

Thank you for your interest in contributing to the Claw Agent Protocol (CAP)! This project aims to solve the data chaos problem for AI agents, and we welcome contributions from the community.

## How to Contribute

### Reporting Issues

If you encounter a bug or have a feature request:

1. Check the [existing issues](https://github.com/jfleagl12/claw-agent-protocol/issues) to avoid duplicates
2. Open a new issue with a clear title and description
3. Include steps to reproduce (for bugs) or use cases (for features)
4. Add relevant labels (bug, enhancement, documentation, etc.)

### Contributing Code

We welcome pull requests for bug fixes, new connectors, documentation improvements, and new features.

#### Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/claw-agent-protocol.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes thoroughly
6. Commit with clear messages: `git commit -m "Add feature: description"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

#### Code Standards

- Follow PEP 8 style guidelines for Python code
- Use type hints where appropriate
- Add docstrings to all public functions and classes
- Keep functions focused and modular
- Write clear commit messages

#### Testing

Before submitting a PR:

- Test your changes locally
- Ensure existing functionality still works
- Add tests for new features (when applicable)
- Run linting: `ruff check .` (if you have ruff installed)

### Building New Connectors

One of the most valuable contributions is adding support for new data sources. To build a connector:

1. Read the [Connector Guide](docs/connectors.md)
2. Inherit from `CAPConnector` base class
3. Implement required methods (`authenticate`, `get_supported_shelves`, `fetch_*`)
4. Normalize data to the CAP schema
5. Add documentation and examples
6. Submit a PR with your connector

**Popular connector requests:**
- Notion
- Slack
- Microsoft Outlook
- Apple Calendar/Contacts
- Todoist
- Linear

### Documentation

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add examples and use cases
- Improve setup instructions
- Translate documentation (future)

### Community Guidelines

- Be respectful and constructive
- Help others in issues and discussions
- Share your use cases and feedback
- Celebrate contributions from others

## Development Setup

```bash
# Clone the repo
git clone https://github.com/jfleagl12/claw-agent-protocol.git
cd claw-agent-protocol

# Install in development mode
pip install -e ".[dev]"

# Run tests (when available)
pytest

# Run linting
ruff check .
black --check .
```

## Questions?

- Open a [Discussion](https://github.com/jfleagl12/claw-agent-protocol/discussions) for questions
- Check the [Documentation](docs/)
- Reach out to [@jfleagl12](https://github.com/jfleagl12)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
