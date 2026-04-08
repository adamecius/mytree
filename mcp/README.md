# MCP module

## Why this module exists
This folder isolates Model Context Protocol-style capabilities so tool exposure can evolve independently from HTTP routes.

## Files
- `server.py`: tool registry and helper methods to list available tools.
- `tools/`: concrete tool implementations.

## Function one-liners
- `list_tools()`: returns sorted MCP tool identifiers.
