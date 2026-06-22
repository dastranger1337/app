# AXIOM Static Web App

A standalone browser-based UI for the AXIOM red-team interface.

## Overview

This app is a static HTML/JavaScript prototype built from the supplied AXIOM UI design.
It includes:
- Chat interface with AI provider configuration
- Terminal sandbox with optional backend execution
- Ops dashboard and system stats
- Intel analysis panel
- Arsenal file/tool panel
- Agent spawn and management UI
- Build planner and export utilities
- God Mode + auto-exec toggles

## Run locally

### Option 1: Open directly

Open `index.html` in a browser.

### Option 2: Run a local server

```bash
python3 -m http.server 8000
```

Open `http://127.0.0.1:8000` in your browser.

## Configuration

## Configuration

Use the CONFIG panel to set:
- `Anthropic` or custom API key
- backend execution URL
- backend token
- selected model and system prompt

Saved settings are persisted in browser local storage.

## Notes

- This app is a front-end prototype and does not include a bundled backend server.
- Backend execution requires a compatible `/exec` endpoint returning JSON with `stdout`, `stderr`, and `exitCode`.
- The UI is designed for offline preview and integration into a larger AXIOM system.
