# CAP Connector Guide

Connectors are the modules that power the CAP MCP server. They are responsible for fetching data from external APIs and normalizing it to the CAP schema in real-time.

## Core Concepts

-   **On-Demand**: Connectors do not continuously sync data. They fetch it only when an agent makes a request.
-   **Stateless**: Connectors do not store data themselves. They are a pass-through translation layer.
-   **Authentication-Aware**: Connectors manage the OAuth tokens and credentials needed to access external APIs.

## Building a New Connector

To build a new connector, you need to create a Python class that inherits from the `CAPConnector` base class.

### 1. Inherit from `CAPConnector`

```python
from cap.connectors.base import CAPConnector

class MySourceConnector(CAPConnector):
    # ... implementation ...
```

### 2. Implement `authenticate()`

This method is responsible for handling the authentication with the external service. For most modern services, this will involve an OAuth 2.0 flow.

```python
async def authenticate(self) -> bool:
    # 1. Check if we already have a valid token.
    # 2. If not, initiate the OAuth flow.
    # 3. Store the new token securely.
    # 4. Return True on success.
    pass
```

### 3. Implement `get_supported_shelves()`

This method tells the CAP server which data shelves your connector can provide.

```python
def get_supported_shelves(self) -> List[str]:
    return ["docs", "tasks"]
```

### 4. Implement Shelf-Specific Fetch Methods

For each shelf your connector supports, you must implement the corresponding `fetch_*` method. For example, for the `docs` shelf:

```python
async def fetch_docs(self, query: Optional[str] = None, limit: int = 50) -> List[Dict]:
    # 1. Ensure the connector is authenticated.
    await self.authenticate()

    # 2. Make the API call to the external source.
    raw_data = await self.source_api.search(query=query, limit=limit)

    # 3. Normalize the raw data to the CAP schema.
    normalized_docs = [self._normalize_doc(item) for item in raw_data]

    return normalized_docs
```

### 5. Implement Normalization

Normalization is the process of converting the proprietary data structure from the source API into the clean, canonical CAP schema.

```python
def _normalize_doc(self, raw_item: Dict) -> Dict:
    return {
        "id": raw_item.get("id"),
        "type": "note",
        "title": raw_item.get("title"),
        "content_preview": raw_item.get("excerpt", ""),
        "url": raw_item.get("web_url"),
        "updated_at": raw_item.get("last_edited_time"),
        "source": self.create_source_pointer(raw_item, raw_item.get("id"))
    }
```

### 6. Register the Connector

Finally, add your new connector to the `ConnectorRegistry` in `src/cap/connectors/registry.py` so that the server can discover and use it.

## Caching

To improve performance and avoid hitting API rate limits, the CAP server provides a built-in caching layer. Your connector does not need to implement caching itself; simply return the data, and the server will handle caching it appropriately.

## Error Handling

Your connector should be robust to API failures. If an external API call fails, your `fetch_*` method should raise an exception. The server will catch this, log the error, and continue to fetch data from other available connectors.
