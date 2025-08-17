#!/usr/bin/env python3
"""
Guardian Seven Best Shows Monitor - CLI Utility
Simple command-line interface for managing the Guardian show monitor.
Designed for single-run execution (e.g., via cron job).
"""

import sys
import os
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_dir))

from main import main as run_main

def print_usage():
    """Print usage information."""
    print("""
Guardian Seven Best Shows Monitor - CLI Utility

Usage:
  ./guardian_monitor.py [command]

Commands:
  run         - Check for new shows and exit (default)
  test        - Test all components
  status      - Show current status
  config      - Show configuration
  help        - Show this help message

Examples:
  ./guardian_monitor.py           # Check for new shows
  ./guardian_monitor.py test      # Test Discord and other components
  ./guardian_monitor.py status    # Show current status

Configuration:
  Create a .env file in the project root with:
  DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

  Modify config.ini to customize application behavior.

Scheduling:
  Add to crontab to run every hour:
  0 * * * * cd /path/to/guardian-seven-best-shows-monitor && ./guardian_monitor.py

For more information, see the README.md file.
""")

def main():
    """Main CLI entry point."""
    # Get command from arguments
    command = sys.argv[1] if len(sys.argv) > 1 else 'run'
    
    # Handle help command
    if command in ['help', '-h', '--help']:
        print_usage()
        return
    
    # Map commands to main.py arguments
    command_map = {
        'run': [],           # Default: just run once
        'test': ['--test'],
        'status': ['--status'],
        'config': ['--config']
    }
    
    if command not in command_map:
        print(f"❌ Unknown command: {command}")
        print_usage()
        sys.exit(1)
    
    # Set up sys.argv for main.py
    sys.argv = ['main.py'] + command_map[command]
    
    # Run the main application
    try:
        run_main()
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
