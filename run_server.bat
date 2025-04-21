@echo off
REM Simple script to run the Stemformatics MCP server on Windows

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is required but not installed.
    exit /b 1
)

REM Check if virtual environment exists, create if it doesn't
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if config file exists
if not exist config.json (
    if exist config.example.json (
        echo Config file not found. Creating from example...
        copy config.example.json config.json
        echo Please edit config.json with your API settings.
    )
)

REM Run the server with MCP CLI
echo Starting Stemformatics MCP Server...
python -m mcp dev server.py

REM Deactivate virtual environment on exit
deactivate 