#!/usr/bin/env python3
"""
Stemformatics MCP Demo Client

This is a simple client that demonstrates how to interact with the Stemformatics MCP server.
It's useful for testing and exploring the server's capabilities.
"""

import sys
import json
import subprocess
import argparse
from typing import Dict, Any, List

def run_mcp_command(server_process, command: Dict[str, Any]) -> Dict[str, Any]:
    """Send a command to the MCP server and get the response"""
    # Convert command to JSON and send to server
    command_json = json.dumps(command) + "\n"
    server_process.stdin.write(command_json.encode("utf-8"))
    server_process.stdin.flush()
    
    # Read the response
    response_json = server_process.stdout.readline().decode("utf-8").strip()
    response = json.loads(response_json)
    return response

def main():
    parser = argparse.ArgumentParser(description="Stemformatics MCP Demo Client")
    parser.add_argument("--server", default="./server.py", help="Path to the MCP server script")
    parser.add_argument("--config", default="config.json", help="Path to the config file")
    args = parser.parse_args()
    
    print("Starting Stemformatics MCP Demo Client")
    print(f"Server: {args.server}")
    print(f"Config: {args.config}")
    
    # Start the server as a subprocess
    server_process = subprocess.Popen(
        [sys.executable, args.server],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={"CONFIG_PATH": args.config, "MCP_TRANSPORT": "stdio"}
    )
    
    # Check if server is running
    init_message = server_process.stdout.readline().decode("utf-8").strip()
    if not init_message:
        print("Error: Failed to start MCP server")
        stderr = server_process.stderr.read().decode("utf-8")
        print(f"Server error: {stderr}")
        return
    
    print(f"Server started: {init_message}")
    
    try:
        # Send a handshake message
        handshake = {
            "id": "1",
            "type": "handshake",
            "version": "0.4",
            "capabilities": ["tools", "resources"]
        }
        
        response = run_mcp_command(server_process, handshake)
        print("\n=== Handshake Response ===")
        print(json.dumps(response, indent=2))
        
        # Get server info
        info_request = {
            "id": "2",
            "type": "info"
        }
        
        response = run_mcp_command(server_process, info_request)
        print("\n=== Server Info ===")
        print(json.dumps(response, indent=2))
        
        # Test list_datasets tool
        list_datasets_request = {
            "id": "3",
            "type": "tool",
            "name": "list_datasets",
            "parameters": {"limit": 5}
        }
        
        response = run_mcp_command(server_process, list_datasets_request)
        print("\n=== List Datasets Response ===")
        print(json.dumps(response, indent=2))
        
        # Test datasets resource
        datasets_resource_request = {
            "id": "4",
            "type": "resource",
            "uri": "datasets://all"
        }
        
        response = run_mcp_command(server_process, datasets_resource_request)
        print("\n=== Datasets Resource Response ===")
        print(json.dumps(response, indent=2))
        
        # Interactive mode
        print("\n=== Interactive Mode ===")
        print("Enter commands in JSON format, or 'exit' to quit")
        
        while True:
            command_str = input("> ")
            if command_str.lower() == "exit":
                break
                
            try:
                command = json.loads(command_str)
                response = run_mcp_command(server_process, command)
                print(json.dumps(response, indent=2))
            except json.JSONDecodeError:
                print("Error: Invalid JSON")
            except Exception as e:
                print(f"Error: {e}")
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Terminate the server process
        server_process.terminate()
        
if __name__ == "__main__":
    main() 