#!/usr/bin/env python3
"""
Demo script to show qBittorrent restart functionality when new shows are added
"""

import sys
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_dir))

from qbittorrent_rules import QBittorrentRulesManager

def demo_restart_functionality():
    """Demonstrate the qBittorrent restart functionality."""
    manager = QBittorrentRulesManager()
    
    print("=== qBittorrent Restart Functionality Demo ===")
    print()
    
    # Check initial status
    initial_running = manager.is_qbittorrent_running()
    print(f"1. Initial qBittorrent status: {'Running' if initial_running else 'Not running'}")
    
    if not initial_running:
        print("   Starting qBittorrent for demo...")
        if manager.start_qbittorrent():
            print("   ✅ qBittorrent started")
        else:
            print("   ❌ Failed to start qBittorrent")
            return
    
    print()
    print("2. Simulating the Guardian monitor adding new shows...")
    print("   This is what happens when the main Guardian monitor finds new shows:")
    print()
    
    # Simulate the process that happens in main.py _manage_qbittorrent_rules
    print("   a) Guardian monitor detects new shows")
    print("   b) Checks if qBittorrent is running...")
    
    was_running = manager.is_qbittorrent_running()
    print(f"      → qBittorrent is {'running' if was_running else 'not running'}")
    
    if was_running:
        print("   c) Closes qBittorrent to safely modify rules...")
        if manager.close_qbittorrent():
            print("      ✅ qBittorrent closed successfully")
        else:
            print("      ❌ Failed to close qBittorrent")
            return
        
        print("   d) Creates backup of existing rules")
        print("   e) Adds new download rules for the shows")
        print("   f) Saves updated rules to qBittorrent config")
        
        print("   g) Restarts qBittorrent...")
        if manager.start_qbittorrent():
            print("      ✅ qBittorrent restarted successfully")
            print("      → New rules are now active and ready to download")
        else:
            print("      ❌ Failed to restart qBittorrent")
    
    print()
    print("3. Final status:")
    final_running = manager.is_qbittorrent_running()
    print(f"   qBittorrent is {'running' if final_running else 'not running'}")
    
    print()
    print("📝 Summary:")
    print("   - The Guardian monitor automatically manages qBittorrent")
    print("   - When new shows are found, it:")
    print("     1. Closes qBittorrent (if running)")
    print("     2. Creates backup of rules")
    print("     3. Adds new download rules")
    print("     4. Restarts qBittorrent (if it was running)")
    print("   - This ensures new rules are loaded and active")
    print()
    print("🔧 The restart happens automatically in the main Guardian monitor")
    print("   when new shows are detected and processed.")

if __name__ == "__main__":
    demo_restart_functionality()
