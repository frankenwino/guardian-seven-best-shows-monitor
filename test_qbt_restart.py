#!/usr/bin/env python3
"""
Test script to verify qBittorrent restart behavior
"""

import sys
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_dir))

from qbittorrent_rules import QBittorrentRulesManager

def test_restart():
    """Test qBittorrent restart functionality."""
    manager = QBittorrentRulesManager()
    
    print("=== qBittorrent Restart Test ===")
    
    # Check initial status
    initial_running = manager.is_qbittorrent_running()
    print(f"Initial status: {'Running' if initial_running else 'Not running'}")
    
    if initial_running:
        print("\n1. Testing close...")
        if manager.close_qbittorrent():
            print("✅ Successfully closed qBittorrent")
            
            print("\n2. Testing restart...")
            if manager.start_qbittorrent():
                print("✅ Successfully restarted qBittorrent")
            else:
                print("❌ Failed to restart qBittorrent")
        else:
            print("❌ Failed to close qBittorrent")
    else:
        print("\n1. Testing start...")
        if manager.start_qbittorrent():
            print("✅ Successfully started qBittorrent")
            
            print("\n2. Testing close...")
            if manager.close_qbittorrent():
                print("✅ Successfully closed qBittorrent")
            else:
                print("❌ Failed to close qBittorrent")
        else:
            print("❌ Failed to start qBittorrent")
    
    # Final status
    final_running = manager.is_qbittorrent_running()
    print(f"\nFinal status: {'Running' if final_running else 'Not running'}")

if __name__ == "__main__":
    test_restart()
