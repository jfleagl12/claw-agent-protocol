#!/usr/bin/env python3
"""
CAP MCP Server - Main Entry Point

The Claw Agent Protocol (CAP) MCP server provides canonical access to personal data
across multiple sources through a standardized schema.
"""

from typing import Any, Dict, List, Optional
import logging
from mcp.server.fastmcp import FastMCP
from cap.connectors.registry import ConnectorRegistry
from cap.server.cache import CacheManager
from cap.server.config import ServerConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # Log to stderr only (MCP requirement)
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("claw-agent-protocol", version="2.0.0")

# Initialize components
config = ServerConfig.from_env()
registry = ConnectorRegistry(config)
cache = CacheManager(config.cache_ttl)


# ============================================================================
# RESOURCES (Canonical Shelves)
# ============================================================================

@mcp.resource("cap://identity")
async def get_identity_shelf(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Access the identity shelf containing people, organizations, and contacts.
    
    Args:
        filters: Optional filters (e.g., {"type": "person", "tags": ["client"]})
    
    Returns:
        Canonical identity data from all connected sources
    """
    logger.info("Fetching identity shelf")
    
    # Check cache
    cache_key = f"identity:{str(filters)}"
    if cached := await cache.get(cache_key):
        logger.info("Returning cached identity data")
        return cached
    
    # Fetch from connectors
    results = []
    for connector in registry.get_connectors_for_shelf("identity"):
        try:
            data = await connector.fetch_identity(filters)
            results.extend(data)
        except Exception as e:
            logger.error(f"Error fetching from {connector.name}: {e}")
    
    # Cache and return
    await cache.set(cache_key, results)
    return {"shelf": "identity", "count": len(results), "items": results}


@mcp.resource("cap://calendar")
async def get_calendar_shelf(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Access the calendar shelf containing events and availability.
    
    Args:
        start_date: ISO8601 date string (default: today)
        end_date: ISO8601 date string (default: 30 days from start)
    
    Returns:
        Canonical calendar data from all connected sources
    """
    logger.info(f"Fetching calendar shelf: {start_date} to {end_date}")
    
    cache_key = f"calendar:{start_date}:{end_date}"
    if cached := await cache.get(cache_key):
        return cached
    
    results = []
    for connector in registry.get_connectors_for_shelf("calendar"):
        try:
            data = await connector.fetch_calendar(start_date, end_date)
            results.extend(data)
        except Exception as e:
            logger.error(f"Error fetching from {connector.name}: {e}")
    
    # Sort by start time
    results.sort(key=lambda x: x.get("start_time", ""))
    
    await cache.set(cache_key, results)
    return {"shelf": "calendar", "count": len(results), "items": results}


@mcp.resource("cap://comms")
async def get_comms_shelf(
    since: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Access the comms shelf containing messages, emails, and threads.
    
    Args:
        since: ISO8601 timestamp (default: last 7 days)
        limit: Maximum number of items to return
    
    Returns:
        Canonical communications data from all connected sources
    """
    logger.info(f"Fetching comms shelf: since={since}, limit={limit}")
    
    cache_key = f"comms:{since}:{limit}"
    if cached := await cache.get(cache_key):
        return cached
    
    results = []
    for connector in registry.get_connectors_for_shelf("comms"):
        try:
            data = await connector.fetch_comms(since, limit)
            results.extend(data)
        except Exception as e:
            logger.error(f"Error fetching from {connector.name}: {e}")
    
    # Sort by timestamp (newest first)
    results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    results = results[:limit]
    
    await cache.set(cache_key, results)
    return {"shelf": "comms", "count": len(results), "items": results}


@mcp.resource("cap://docs")
async def get_docs_shelf(
    query: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Access the docs shelf containing notes, files, and snippets.
    
    Args:
        query: Optional search query
        limit: Maximum number of items to return
    
    Returns:
        Canonical documents data from all connected sources
    """
    logger.info(f"Fetching docs shelf: query={query}, limit={limit}")
    
    cache_key = f"docs:{query}:{limit}"
    if cached := await cache.get(cache_key):
        return cached
    
    results = []
    for connector in registry.get_connectors_for_shelf("docs"):
        try:
            data = await connector.fetch_docs(query, limit)
            results.extend(data)
        except Exception as e:
            logger.error(f"Error fetching from {connector.name}: {e}")
    
    results = results[:limit]
    
    await cache.set(cache_key, results)
    return {"shelf": "docs", "count": len(results), "items": results}


@mcp.resource("cap://tasks")
async def get_tasks_shelf(
    status: Optional[List[str]] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Access the tasks shelf containing tasks, projects, and milestones.
    
    Args:
        status: Filter by status (e.g., ["active", "pending"])
        limit: Maximum number of items to return
    
    Returns:
        Canonical tasks data from all connected sources
    """
    logger.info(f"Fetching tasks shelf: status={status}, limit={limit}")
    
    cache_key = f"tasks:{str(status)}:{limit}"
    if cached := await cache.get(cache_key):
        return cached
    
    results = []
    for connector in registry.get_connectors_for_shelf("tasks"):
        try:
            data = await connector.fetch_tasks(status, limit)
            results.extend(data)
        except Exception as e:
            logger.error(f"Error fetching from {connector.name}: {e}")
    
    # Sort by due date
    results.sort(key=lambda x: x.get("due_date") or "9999-12-31")
    results = results[:limit]
    
    await cache.set(cache_key, results)
    return {"shelf": "tasks", "count": len(results), "items": results}


# ============================================================================
# TOOLS (Task-Oriented Views)
# ============================================================================

@mcp.tool()
async def today_briefing() -> str:
    """
    Get a comprehensive briefing for today including calendar events, 
    due tasks, and recent communications.
    
    Returns:
        Formatted briefing text
    """
    logger.info("Generating today briefing")
    
    from datetime import datetime, timedelta
    today = datetime.now().date().isoformat()
    tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
    
    # Fetch data
    calendar = await get_calendar_shelf(start_date=today, end_date=tomorrow)
    tasks = await get_tasks_shelf(status=["active", "pending"])
    comms = await get_comms_shelf(since=today, limit=10)
    
    # Format briefing
    briefing = f"# Today's Briefing - {today}\n\n"
    
    # Calendar events
    briefing += f"## Calendar ({calendar['count']} events)\n\n"
    for event in calendar['items']:
        briefing += f"- {event.get('start_time', 'TBD')}: {event.get('title', 'Untitled')}\n"
    
    # Due tasks
    due_today = [t for t in tasks['items'] if t.get('due_date', '') <= today]
    briefing += f"\n## Tasks Due Today ({len(due_today)})\n\n"
    for task in due_today[:10]:
        briefing += f"- [{task.get('status', '?')}] {task.get('title', 'Untitled')}\n"
    
    # Recent comms
    briefing += f"\n## Recent Communications ({comms['count']})\n\n"
    for comm in comms['items'][:5]:
        briefing += f"- From {comm.get('from', 'Unknown')}: {comm.get('subject', 'No subject')}\n"
    
    return briefing


@mcp.tool()
async def client_pipeline(client_tag: Optional[str] = None) -> str:
    """
    Get an overview of client relationships including contacts, communications, and tasks.
    
    Args:
        client_tag: Optional tag to filter clients (default: all clients)
    
    Returns:
        Formatted client pipeline report
    """
    logger.info(f"Generating client pipeline: tag={client_tag}")
    
    # Fetch data
    identity = await get_identity_shelf(filters={"type": "person", "tags": ["client"]})
    comms = await get_comms_shelf(limit=50)
    tasks = await get_tasks_shelf(limit=100)
    
    report = "# Client Pipeline\n\n"
    
    for client in identity['items']:
        if client_tag and client_tag not in client.get('tags', []):
            continue
        
        name = client.get('name_display', 'Unknown')
        report += f"## {name}\n\n"
        
        # Recent comms with this client
        client_comms = [c for c in comms['items'] if c.get('from') == client.get('id')]
        report += f"- Recent communications: {len(client_comms)}\n"
        
        # Tasks related to this client
        client_tasks = [t for t in tasks['items'] if name.lower() in t.get('title', '').lower()]
        report += f"- Related tasks: {len(client_tasks)}\n\n"
    
    return report


@mcp.tool()
async def knowledge_search(query: str, limit: int = 10) -> str:
    """
    Search across all documents and notes.
    
    Args:
        query: Search query string
        limit: Maximum number of results
    
    Returns:
        Formatted search results
    """
    logger.info(f"Knowledge search: query={query}, limit={limit}")
    
    docs = await get_docs_shelf(query=query, limit=limit)
    
    results = f"# Search Results for '{query}'\n\n"
    results += f"Found {docs['count']} results\n\n"
    
    for doc in docs['items']:
        results += f"## {doc.get('title', 'Untitled')}\n"
        results += f"Type: {doc.get('type', 'unknown')} | Updated: {doc.get('updated_at', 'N/A')}\n"
        if preview := doc.get('content_preview'):
            results += f"{preview}...\n"
        results += "\n"
    
    return results


# ============================================================================
# SERVER LIFECYCLE
# ============================================================================

def main():
    """Main entry point for CAP MCP server."""
    logger.info("Starting CAP MCP Server v2.0")
    logger.info(f"Enabled connectors: {config.enabled_connectors}")
    
    # Initialize connectors
    registry.initialize()
    
    # Run the server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
