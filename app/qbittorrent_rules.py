#!/usr/bin/env python3
"""
qBittorrent Download Rules Manager for Guardian Shows

This script helps manage qBittorrent RSS download rules for shows
discovered by the Guardian Seven Best Shows Monitor.
"""

import json
import os
import shutil
import subprocess
import time
import gzip
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QBittorrentRulesManager:
    def __init__(self, rules_file_path: str = None):
        """Initialize the rules manager."""
        if rules_file_path is None:
            # Default qBittorrent config path
            home = Path.home()
            self.rules_file = home / ".config" / "qBittorrent" / "rss" / "download_rules.json"
        else:
            self.rules_file = Path(rules_file_path)
        
        self.backup_dir = Path.home() / ".config" / "qBittorrent" / "rss" / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def is_qbittorrent_running(self) -> bool:
        """Check if qBittorrent is currently running."""
        try:
            # Check for qbittorrent process
            result = subprocess.run(['pgrep', '-f', 'qbittorrent'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Could not check qBittorrent status: {e}")
            return False
    
    def close_qbittorrent(self) -> bool:
        """Close qBittorrent gracefully."""
        if not self.is_qbittorrent_running():
            logger.info("qBittorrent is not running")
            return True
        
        try:
            logger.info("Closing qBittorrent...")
            # Try graceful shutdown first
            subprocess.run(['pkill', '-TERM', 'qbittorrent'], check=False)
            
            # Wait up to 10 seconds for graceful shutdown
            for i in range(10):
                time.sleep(1)
                if not self.is_qbittorrent_running():
                    logger.info("qBittorrent closed gracefully")
                    return True
                logger.info(f"Waiting for qBittorrent to close... ({i+1}/10)")
            
            # Force kill if still running
            logger.warning("Force closing qBittorrent...")
            subprocess.run(['pkill', '-KILL', 'qbittorrent'], check=False)
            time.sleep(2)
            
            if not self.is_qbittorrent_running():
                logger.info("qBittorrent force closed")
                return True
            else:
                logger.error("Failed to close qBittorrent")
                return False
                
        except Exception as e:
            logger.error(f"Error closing qBittorrent: {e}")
            return False
    
    def start_qbittorrent(self) -> bool:
        """Start qBittorrent."""
        if self.is_qbittorrent_running():
            logger.info("qBittorrent is already running")
            return True
        
        try:
            logger.info("Starting qBittorrent...")
            # Start qBittorrent in background
            subprocess.Popen(['qbittorrent'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            # Wait up to 15 seconds for startup
            for i in range(15):
                time.sleep(1)
                if self.is_qbittorrent_running():
                    logger.info("qBittorrent started successfully")
                    return True
                logger.info(f"Waiting for qBittorrent to start... ({i+1}/15)")
            
            logger.error("qBittorrent failed to start within 15 seconds")
            return False
            
        except Exception as e:
            logger.error(f"Error starting qBittorrent: {e}")
            return False
        
    def backup_rules(self) -> Path:
        """Create a compressed backup of the current rules file."""
        if not self.rules_file.exists():
            raise FileNotFoundError(f"Rules file not found: {self.rules_file}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"download_rules_backup_{timestamp}.json.gz"
        
        # Create compressed backup
        with open(self.rules_file, 'rb') as f_in:
            with gzip.open(backup_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        logger.info(f"Compressed backup created: {backup_file}")
        
        # Clean up old backups - keep only 10 most recent
        self._cleanup_old_backups()
        
        return backup_file
    
    def _cleanup_old_backups(self, max_backups: int = 10) -> None:
        """Clean up old backup files, keeping only the most recent ones."""
        try:
            # Get all backup files (both compressed and uncompressed)
            backup_patterns = ["download_rules_backup_*.json", "download_rules_backup_*.json.gz"]
            backup_files = []
            for pattern in backup_patterns:
                backup_files.extend(list(self.backup_dir.glob(pattern)))
            
            if len(backup_files) <= max_backups:
                return  # No cleanup needed
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Keep only the most recent max_backups files
            files_to_keep = backup_files[:max_backups]
            files_to_delete = backup_files[max_backups:]
            
            # Delete old backup files
            deleted_count = 0
            for backup_file in files_to_delete:
                try:
                    backup_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old backup: {backup_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to delete backup {backup_file.name}: {e}")
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old backup files, kept {len(files_to_keep)} most recent")
                
        except Exception as e:
            logger.warning(f"Error during backup cleanup: {e}")
    
    def show_backup_status(self) -> None:
        """Show status of backup files."""
        try:
            # Get all backup files (both compressed and uncompressed)
            backup_patterns = ["download_rules_backup_*.json", "download_rules_backup_*.json.gz"]
            backup_files = []
            for pattern in backup_patterns:
                backup_files.extend(list(self.backup_dir.glob(pattern)))
            
            print("=== qBittorrent Rules Backup Status ===")
            print(f"Backup directory: {self.backup_dir}")
            print(f"Total backup files: {len(backup_files)}")
            
            if not backup_files:
                print("No backup files found")
                return
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Calculate total size and compression stats
            total_size = sum(f.stat().st_size for f in backup_files)
            total_size_mb = total_size / (1024 * 1024)
            
            compressed_files = [f for f in backup_files if f.name.endswith('.gz')]
            uncompressed_files = [f for f in backup_files if not f.name.endswith('.gz')]
            
            print(f"Total size: {total_size_mb:.2f} MB")
            print(f"Compressed files: {len(compressed_files)}")
            print(f"Uncompressed files: {len(uncompressed_files)}")
            print(f"Max backups kept: 10")
            
            if len(backup_files) > 10:
                print(f"⚠️  {len(backup_files) - 10} old backups can be cleaned up")
            else:
                print("✅ Backup count within limit")
            
            print("\nRecent backup files:")
            for i, backup_file in enumerate(backup_files[:5]):  # Show 5 most recent
                size_kb = backup_file.stat().st_size / 1024
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                compression_info = " (compressed)" if backup_file.name.endswith('.gz') else " (uncompressed)"
                print(f"  {i+1}. {backup_file.name} ({size_kb:.1f} KB{compression_info}, {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
            
            if len(backup_files) > 5:
                print(f"  ... and {len(backup_files) - 5} more")
                
        except Exception as e:
            logger.error(f"Error showing backup status: {e}")
    
    def cleanup_backups(self, max_backups: int = 10) -> None:
        """Manually clean up old backup files."""
        try:
            # Get all backup files (both compressed and uncompressed)
            backup_patterns = ["download_rules_backup_*.json", "download_rules_backup_*.json.gz"]
            backup_files = []
            for pattern in backup_patterns:
                backup_files.extend(list(self.backup_dir.glob(pattern)))
            
            print("=== Cleaning Up Old Backup Files ===")
            print(f"Found {len(backup_files)} backup files")
            
            if len(backup_files) <= max_backups:
                print(f"✅ Only {len(backup_files)} files found, no cleanup needed (max: {max_backups})")
                return
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            files_to_keep = backup_files[:max_backups]
            files_to_delete = backup_files[max_backups:]
            
            print(f"Keeping {len(files_to_keep)} most recent files")
            print(f"Deleting {len(files_to_delete)} old files:")
            
            deleted_count = 0
            freed_space = 0
            
            for backup_file in files_to_delete:
                try:
                    file_size = backup_file.stat().st_size
                    compression_info = " (compressed)" if backup_file.name.endswith('.gz') else " (uncompressed)"
                    backup_file.unlink()
                    deleted_count += 1
                    freed_space += file_size
                    print(f"  ✅ Deleted: {backup_file.name}{compression_info}")
                except Exception as e:
                    print(f"  ❌ Failed to delete {backup_file.name}: {e}")
            
            freed_space_mb = freed_space / (1024 * 1024)
            print(f"\n🎉 Cleanup complete:")
            print(f"   Deleted: {deleted_count} files")
            print(f"   Freed space: {freed_space_mb:.2f} MB")
            print(f"   Remaining: {len(files_to_keep)} backup files")
            
        except Exception as e:
            logger.error(f"Error during manual backup cleanup: {e}")
    
    def load_rules(self) -> Dict:
        """Load existing qBittorrent rules."""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading rules: {e}")
            raise
    
    def save_rules(self, rules: Dict) -> None:
        """Save rules back to qBittorrent config."""
        try:
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(rules, f, indent=4, ensure_ascii=False)
            logger.info(f"Rules saved to: {self.rules_file}")
        except Exception as e:
            logger.error(f"Error saving rules: {e}")
            raise
    
    def get_guardian_shows(self) -> List[Dict]:
        """Get shows from Guardian monitor data."""
        try:
            guardian_data_file = Path(__file__).parent.parent / "data" / "shows_history.json"
            
            if not guardian_data_file.exists():
                logger.warning("No Guardian data found")
                return []
            
            with open(guardian_data_file, 'r') as f:
                history = json.load(f)
            
            # Extract unique shows
            shows = {}
            for entry in history:
                for show in entry['shows']:
                    title = show['title']
                    if title not in shows:
                        shows[title] = {
                            'title': title,
                            'platform': show.get('platform', 'Unknown'),
                            'pick_of_the_week': show.get('pick_of_the_week', False),
                            'description': show.get('description', '')[:100] + '...' if show.get('description') else ''
                        }
            
            return list(shows.values())
            
        except Exception as e:
            logger.error(f"Error loading Guardian shows: {e}")
            return []
    
    def check_existing_rules(self, show_title: str, existing_rules: Dict) -> List[str]:
        """Check if a show already has rules (exact match only)."""
        matches = []
        
        # Exact match only
        if show_title in existing_rules:
            matches.append(f"Exact: {show_title}")
        
        return matches
    
    def clean_title_for_search(self, title: str) -> str:
        """Clean show title for search - remove punctuation and special characters."""
        import re
        # Remove all punctuation and special characters, keep only alphanumeric and spaces
        cleaned = re.sub(r'[^\w\s]', '', title)
        # Replace multiple spaces with single space and strip
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def create_rule_template(self, show_title: str, platform: str = "Unknown") -> Dict:
        """Create a new download rule template for a show."""
        # Clean title for mustContain (no punctuation + 1080)
        clean_title = self.clean_title_for_search(show_title)
        must_contain = f"{clean_title} 1080"
        
        # Create tags based on title word count
        # If title is one word: [title, "Guardian Best Shows"]
        # If title is multiple words: ["Guardian Best Shows"] only
        title_words = clean_title.split()
        if len(title_words) == 1:
            tags = [clean_title, "Guardian Best Shows"]
        else:
            tags = ["Guardian Best Shows"]
        
        return {
            "addPaused": None,
            "affectedFeeds": [
                "https://eztv.re/ezrss.xml",
                "https://www.torrentfunk.com/television/rss.xml"
            ],
            "assignedCategory": "AlexTV",
            "enabled": True,  # Enable rules automatically
            "episodeFilter": "1x1-;",
            "ignoreDays": 0,
            "lastMatch": "",
            "mustContain": must_contain,
            "mustNotContain": "",
            "previouslyMatchedEpisodes": [],
            "priority": 0,
            "savePath": "",
            "smartFilter": False,
            "torrentContentLayout": None,
            "torrentParams": {
                "category": "AlexTV",
                "download_limit": -1,
                "download_path": "",
                "inactive_seeding_time_limit": 0,  # Don't seed
                "operating_mode": "AutoManaged",
                "ratio_limit": 0,  # Don't seed
                "save_path": "",
                "seeding_time_limit": 0,  # Don't seed
                "skip_checking": False,
                "tags": tags,
                "upload_limit": -1,
                "use_auto_tmm": True
            },
            "useRegex": False
        }
    
    def analyze_shows(self) -> None:
        """Analyze Guardian shows against existing qBittorrent rules."""
        try:
            rules = self.load_rules()
            guardian_shows = self.get_guardian_shows()
            
            print("=" * 60)
            print("GUARDIAN SHOWS vs qBITTORRENT RULES ANALYSIS")
            print("=" * 60)
            
            if not guardian_shows:
                print("❌ No Guardian shows found. Run the monitor first.")
                return
            
            print(f"\n📊 Found {len(guardian_shows)} unique shows from Guardian data")
            print(f"📊 Found {len(rules)} existing qBittorrent rules")
            
            shows_with_rules = []
            shows_needing_rules = []
            
            for show in guardian_shows:
                title = show['title']
                matches = self.check_existing_rules(title, rules)
                
                if matches:
                    shows_with_rules.append((show, matches))
                else:
                    shows_needing_rules.append(show)
            
            # Shows with existing rules
            if shows_with_rules:
                print(f"\n✅ SHOWS WITH EXISTING RULES ({len(shows_with_rules)}):")
                for show, matches in shows_with_rules:
                    print(f"\n  📺 {show['title']}")
                    print(f"     Platform: {show['platform']}")
                    if show['pick_of_the_week']:
                        print(f"     ⭐ Pick of the week")
                    for match in matches[:3]:  # Show first 3 matches
                        print(f"     → {match}")
            
            # Shows needing rules
            if shows_needing_rules:
                print(f"\n❌ SHOWS NEEDING NEW RULES ({len(shows_needing_rules)}):")
                for show in shows_needing_rules:
                    print(f"\n  📺 {show['title']}")
                    print(f"     Platform: {show['platform']}")
                    if show['pick_of_the_week']:
                        print(f"     ⭐ Pick of the week")
                    if show['description']:
                        print(f"     Description: {show['description']}")
            
            print(f"\n📋 SUMMARY:")
            print(f"   ✅ Shows with rules: {len(shows_with_rules)}")
            print(f"   ❌ Shows needing rules: {len(shows_needing_rules)}")
            print(f"   📊 Total Guardian shows: {len(guardian_shows)}")
            
            if shows_needing_rules:
                print(f"\n💡 TIP: Use 'create-rules' command to generate templates for missing shows")
            
        except Exception as e:
            logger.error(f"Error analyzing shows: {e}")
    
    def create_missing_rules(self, dry_run: bool = True, auto_manage_qbt: bool = False) -> None:
        """Create rules for Guardian shows that don't have them."""
        try:
            rules = self.load_rules()
            guardian_shows = self.get_guardian_shows()
            
            shows_needing_rules = []
            for show in guardian_shows:
                matches = self.check_existing_rules(show['title'], rules)
                if not matches:
                    shows_needing_rules.append(show)
            
            if not shows_needing_rules:
                print("✅ All Guardian shows already have rules!")
                return
            
            if dry_run:
                print("🔍 DRY RUN - No changes will be made")
            else:
                print("🚀 LIVE RUN - Rules will be created")
                
                if auto_manage_qbt:
                    print("\n🔧 Managing qBittorrent process...")
                    
                    # Check if qBittorrent is running
                    was_running = self.is_qbittorrent_running()
                    if was_running:
                        print("📴 qBittorrent is running - closing it...")
                        if not self.close_qbittorrent():
                            print("❌ Failed to close qBittorrent. Please close it manually and try again.")
                            return
                    else:
                        print("✅ qBittorrent is not running")
                    
                    # Double-check it's closed
                    if self.is_qbittorrent_running():
                        print("❌ qBittorrent is still running. Please close it manually and try again.")
                        return
                else:
                    # Manual mode - just warn user
                    if self.is_qbittorrent_running():
                        print("⚠️  WARNING: qBittorrent is running!")
                        print("   Please close qBittorrent before continuing.")
                        response = input("   Continue anyway? (y/N): ").lower().strip()
                        if response != 'y':
                            print("❌ Aborted by user")
                            return
                
                # Create backup first
                backup_file = self.backup_rules()
                print(f"📁 Backup created: {backup_file}")
            
            print(f"\n🔧 {'Would create' if dry_run else 'Creating'} rules for {len(shows_needing_rules)} shows:")
            
            new_rules = rules.copy()
            
            for show in shows_needing_rules:
                title = show['title']
                rule = self.create_rule_template(title, show['platform'])
                clean_title = self.clean_title_for_search(title)
                
                print(f"\n  📺 {title}")
                print(f"     Platform: {show['platform']}")
                if show['pick_of_the_week']:
                    print(f"     ⭐ Pick of the week")
                print(f"     Clean title: '{clean_title}' ({len(clean_title.split())} words)")
                print(f"     Must contain: '{rule['mustContain']}'")
                print(f"     Episode filter: '{rule['episodeFilter']}'")
                print(f"     Category: '{rule['assignedCategory']}'")
                print(f"     Tags: {rule['torrentParams']['tags']} ({'title + Guardian' if len(clean_title.split()) == 1 else 'Guardian only'})")
                print(f"     RSS feeds: {len(rule['affectedFeeds'])} feeds")
                print(f"     Seeding: Disabled (ratio_limit=0)")
                print(f"     Status: {'Would create' if dry_run else 'Created'} (enabled)")
                
                if not dry_run:
                    new_rules[title] = rule
            
            if not dry_run:
                # Save the rules
                self.save_rules(new_rules)
                print(f"\n✅ Successfully added {len(shows_needing_rules)} new rules!")
                print("⚠️  Rules are created ENABLED - they will start downloading automatically")
                
                if auto_manage_qbt:
                    # Restart qBittorrent if it was running
                    if was_running:
                        print("\n🔄 Restarting qBittorrent...")
                        if self.start_qbittorrent():
                            print("✅ qBittorrent restarted successfully")
                            print("💡 New rules are available but disabled - enable them in the UI")
                        else:
                            print("❌ Failed to restart qBittorrent - please start it manually")
                    else:
                        print("💡 qBittorrent was not running - start it manually to see new rules")
                else:
                    print("💡 Restart qBittorrent to see new rules, then enable them in the UI")
            else:
                print(f"\n💡 Run with --apply to actually create the rules")
                if auto_manage_qbt:
                    print("💡 Add --auto-qbt to automatically manage qBittorrent process")
                
        except Exception as e:
            logger.error(f"Error creating rules: {e}")
            if not dry_run and auto_manage_qbt:
                print("🔄 Attempting to restart qBittorrent after error...")
                self.start_qbittorrent()


def main():
    """Main function with command line interface."""
    import sys
    
    manager = QBittorrentRulesManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python qbittorrent_rules.py analyze                    # Analyze shows vs rules")
        print("  python qbittorrent_rules.py create                     # Dry run - show what would be created")
        print("  python qbittorrent_rules.py create --apply             # Create missing rules (manual qBittorrent management)")
        print("  python qbittorrent_rules.py create --apply --auto-qbt  # Create rules with automatic qBittorrent management")
        print("  python qbittorrent_rules.py status                     # Check qBittorrent process status")
        print("  python qbittorrent_rules.py backups                    # Show backup files status")
        print("  python qbittorrent_rules.py cleanup                    # Clean up old backup files")
        return
    
    command = sys.argv[1].lower()
    
    if command == "analyze":
        manager.analyze_shows()
    elif command == "create":
        apply = "--apply" in sys.argv
        auto_qbt = "--auto-qbt" in sys.argv
        manager.create_missing_rules(dry_run=not apply, auto_manage_qbt=auto_qbt)
    elif command == "status":
        print("=== qBittorrent Process Status ===")
        if manager.is_qbittorrent_running():
            print("✅ qBittorrent is running")
        else:
            print("❌ qBittorrent is not running")
    elif command == "backups":
        manager.show_backup_status()
    elif command == "cleanup":
        manager.cleanup_backups()
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
