@echo off
set NPM_CONFIG_CACHE=%CD%\.npm-cache
mkdir .npm-cache 2>nul
npx -y @modelcontextprotocol/inspector ..\.venv\Scripts\python.exe mcp_server.py
