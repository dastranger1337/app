# AXIOM Static Web App

A standalone browser-based prototype for the AXIOM red-team interface.

## Overview

This repository now contains a single static web application built from the supplied AXIOM UI design.
The app includes:
- Chat UI with configurable AI provider support
- Terminal sandbox with optional backend execution
- Ops dashboard, intel analysis, file / arsenal panels
- Agent management and build planning features
- God Mode and auto-exec controls
- Local settings persistence via browser storage

## Run locally

### Option 1: Open directly
Open `new-app/index.html` in your browser.

### Option 2: Run a simple server
```bash
cd /app/new-app
./serve.sh
```
Then visit `http://127.0.0.1:8000`.

### Option 3: Preview on emergent.sh
If emergent.sh supports static preview from this repo, you can deploy using the `app.json` manifest.

## Configuration

Use the CONFIG panel inside the app to set:
- AI key (Anthropic/OpenAI-compatible provider)
- backend execution URL and token
- model, system prompt, token limit, and auto-exec options

## Notes

- This is a front-end prototype. Backend execution requires a compatible `/exec` endpoint.
- Settings are stored in browser local storage for future sessions.

## Repository structure

```
/app/
  new-app/             # Static AXIOM UI prototype
    index.html         # Main app
    README.md          # App usage guide
    serve.sh           # Local web server helper
  LICENSE
  README.md            # This file
  .gitignore
  memory/              # Project memory/docs
```
