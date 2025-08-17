#!/usr/bin/env python3
"""
Log Management Utility for Guardian Seven Best Shows Monitor

Provides commands to manage log files including cleanup and status.
"""

import sys
from pathlib import Path
from datetime import datetime
import logging

class LogManager:
    def __init__(self, log_dir: str = "logs"):
        """Initialize the log manager."""
        self.log_dir = Path(log_dir)
        self.log_pattern = "guardian_monitor_*.log"
    
    def show_log_status(self) -> None:
        """Show status of log files."""
        try:
            log_files = list(self.log_dir.glob(self.log_pattern))
            
            print("=== Guardian Monitor Log Files Status ===")
            print(f"Log directory: {self.log_dir}")
            print(f"Total log files: {len(log_files)}")
            
            if not log_files:
                print("No log files found")
                return
            
            # Sort by modification time (newest first)
            log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in log_files)
            total_size_mb = total_size / (1024 * 1024)
            
            print(f"Total size: {total_size_mb:.2f} MB")
            print(f"Max logs kept: 10")
            
            if len(log_files) > 10:
                print(f"⚠️  {len(log_files) - 10} old log files can be cleaned up")
            else:
                print("✅ Log count within limit")
            
            print("\nRecent log files:")
            for i, log_file in enumerate(log_files[:5]):  # Show 5 most recent
                size_kb = log_file.stat().st_size / 1024
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                print(f"  {i+1}. {log_file.name} ({size_kb:.1f} KB, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
            
            if len(log_files) > 5:
                print(f"  ... and {len(log_files) - 5} more")
                
        except Exception as e:
            print(f"Error showing log status: {e}")
    
    def cleanup_logs(self, max_logs: int = 10) -> None:
        """Clean up old log files."""
        try:
            log_files = list(self.log_dir.glob(self.log_pattern))
            
            print("=== Cleaning Up Old Log Files ===")
            print(f"Found {len(log_files)} log files")
            
            if len(log_files) <= max_logs:
                print(f"✅ Only {len(log_files)} files found, no cleanup needed (max: {max_logs})")
                return
            
            # Sort by modification time (newest first)
            log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            files_to_keep = log_files[:max_logs]
            files_to_delete = log_files[max_logs:]
            
            print(f"Keeping {len(files_to_keep)} most recent files")
            print(f"Deleting {len(files_to_delete)} old files:")
            
            deleted_count = 0
            freed_space = 0
            
            for log_file in files_to_delete:
                try:
                    file_size = log_file.stat().st_size
                    log_file.unlink()
                    deleted_count += 1
                    freed_space += file_size
                    print(f"  ✅ Deleted: {log_file.name}")
                except Exception as e:
                    print(f"  ❌ Failed to delete {log_file.name}: {e}")
            
            freed_space_mb = freed_space / (1024 * 1024)
            print(f"\n🎉 Cleanup complete:")
            print(f"   Deleted: {deleted_count} files")
            print(f"   Freed space: {freed_space_mb:.2f} MB")
            print(f"   Remaining: {len(files_to_keep)} log files")
            
        except Exception as e:
            print(f"Error during log cleanup: {e}")


def main():
    """Main function with command line interface."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python log_manager.py status   # Show log files status")
        print("  python log_manager.py cleanup  # Clean up old log files")
        return
    
    command = sys.argv[1].lower()
    manager = LogManager()
    
    if command == "status":
        manager.show_log_status()
    elif command == "cleanup":
        manager.cleanup_logs()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
