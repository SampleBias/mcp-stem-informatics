@echo off
REM Script to run the Stemformatics MCP Server on Windows

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

REM Check for transport mode
if "%1"=="--network" (
    REM Run in network mode (using SSE transport)
    echo Starting Stemformatics MCP Server in network mode...
    set MCP_TRANSPORT=sse
    python server.py
) else (
    REM Default to stdio mode
    echo Starting Stemformatics MCP Server in stdio mode...
    set MCP_TRANSPORT=stdio
    python server.py
)

REM Deactivate virtual environment on exit
deactivate 