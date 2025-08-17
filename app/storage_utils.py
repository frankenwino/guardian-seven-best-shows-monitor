#!/usr/bin/env python3
"""
Storage utility script for Guardian Seven Best Shows Monitor.
Provides command-line interface for managing stored data.
"""

import argparse
import sys
from storage import ShowDataStorage
from datetime import datetime

def show_stats(storage):
    """Display storage statistics."""
    stats = storage.get_storage_stats()
    
    print("=== Storage Statistics ===")
    print(f"Data Directory: {stats['data_directory']}")
    print(f"Processed Articles: {stats['processed_articles_count']}")
    print(f"History Entries: {stats['shows_history_entries']}")
    
    if 'last_checked_article' in stats:
        last = stats['last_checked_article']
        print(f"Last Checked: {last['title']} ({last['date']})")
        print(f"Checked At: {last['checked_at'][:19]}")
    
    print("\nFile Sizes:")
    for key, value in stats.items():
        if key.endswith('_size_kb'):
            filename = key.replace('_size_kb', '')
            print(f"  {filename}: {value} KB")

def show_history(storage, limit):
    """Display shows history."""
    history = storage.get_shows_history(limit=limit)
    
    print(f"=== Recent History (Last {len(history)} entries) ===")
    for i, entry in enumerate(history, 1):
        print(f"\n{i}. {entry['article_title']}")
        print(f"   Date: {entry['article_date']}")
        print(f"   Shows: {entry['shows_count']}")
        print(f"   URL: {entry['article_url']}")
        
        if len(entry.get('shows', [])) > 0:
            print("   Top shows:")
            for j, show in enumerate(entry['shows'][:3], 1):
                print(f"     {j}. {show['title']} ({show['platform']})")

def search_shows(storage, query):
    """Search for shows."""
    results = storage.search_shows(query, limit=20)
    
    print(f"=== Search Results for '{query}' ===")
    if results:
        for i, show in enumerate(results, 1):
            print(f"\n{i}. {show['title']}")
            print(f"   Platform: {show['platform']}")
            print(f"   From: {show['article_title']} ({show['article_date']})")
            print(f"   Description: {show['description'][:100]}...")
    else:
        print("No results found.")

def filter_by_platform(storage, platform):
    """Filter shows by platform."""
    shows = storage.get_shows_by_platform(platform, limit=20)
    
    print(f"=== Shows on {platform} ===")
    if shows:
        for i, show in enumerate(shows, 1):
            print(f"\n{i}. {show['title']}")
            print(f"   From: {show['article_title']} ({show['article_date']})")
            print(f"   Description: {show['description'][:100]}...")
    else:
        print(f"No shows found on {platform}.")

def cleanup_duplicates(storage):
    """Clean up duplicate entries in shows history."""
    print("Cleaning up duplicate entries in shows history...")
    success = storage.cleanup_duplicate_history_entries()
    
    if success:
        print("✓ Duplicate cleanup completed successfully")
        show_stats(storage)
    else:
        print("✗ Duplicate cleanup failed")

def cleanup_data(storage, days):
    """Clean up old data (optional maintenance - history is kept indefinitely by default)."""
    print(f"Cleaning up data older than {days} days...")
    print("Note: By default, the system keeps all show history to build a comprehensive archive.")
    
    response = input("Are you sure you want to delete old history? (y/N): ")
    if response.lower() != 'y':
        print("Cleanup cancelled - keeping all history")
        return
    
    success = storage.cleanup_old_data(keep_days=days)
    
    if success:
        print("✓ Cleanup completed successfully")
        show_stats(storage)
    else:
        print("✗ Cleanup failed")
    """Clean up old data."""
    print(f"Cleaning up data older than {days} days...")
    success = storage.cleanup_old_data(keep_days=days)
    
    if success:
        print("✓ Cleanup completed successfully")
        show_stats(storage)
    else:
        print("✗ Cleanup failed")

def cleanup_processed_articles(storage, max_articles=100):
    """Clean up old processed articles."""
    print("=== Processed Articles Cleanup ===")
    
    try:
        # Use the storage manager's cleanup method
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent))
        from storage import ShowDataStorage
        
        storage_manager = ShowDataStorage()
        result = storage_manager.cleanup_processed_articles_manual(max_articles)
        
        if result['status'] == 'no_file':
            print("❌ No processed articles file found")
        elif result['status'] == 'no_cleanup_needed':
            print(f"✅ {result['message']}")
        elif result['status'] == 'success':
            print(f"🎉 {result['message']}")
            print(f"   Original count: {result['original_count']}")
            print(f"   Final count: {result['final_count']}")
            print(f"   Removed count: {result['removed_count']}")
            
            # Calculate space saved (rough estimate)
            if result['removed_count'] > 0:
                avg_size_per_article = 50  # bytes (rough estimate)
                space_saved = result['removed_count'] * avg_size_per_article
                print(f"   Estimated space saved: {space_saved} bytes")
        elif result['status'] == 'error':
            print(f"❌ Error: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

def reset_storage(storage):
    """Reset all storage data."""
    import os
    
    confirm = input("Are you sure you want to delete all stored data? (yes/no): ")
    if confirm.lower() == 'yes':
        try:
            for file_path in [storage.last_checked_file, storage.shows_history_file, storage.processed_articles_file]:
                if file_path.exists():
                    os.remove(file_path)
            print("✓ All storage data has been reset")
        except Exception as e:
            print(f"✗ Error resetting data: {e}")
    else:
        print("Reset cancelled")

def main():
    parser = argparse.ArgumentParser(description="Guardian Seven Best Shows Monitor - Storage Utilities")
    parser.add_argument('--data-dir', help='Data directory path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Stats command
    subparsers.add_parser('stats', help='Show storage statistics')
    
    # History command
    history_parser = subparsers.add_parser('history', help='Show shows history')
    history_parser.add_argument('--limit', type=int, default=5, help='Number of entries to show')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for shows')
    search_parser.add_argument('query', help='Search query')
    
    # Platform filter command
    platform_parser = subparsers.add_parser('platform', help='Filter shows by platform')
    platform_parser.add_argument('name', help='Platform name (e.g., Netflix, Disney+)')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old data (optional - history kept indefinitely by default)')
    cleanup_parser.add_argument('--days', type=int, default=90, help='Keep data newer than N days')
    
    # Duplicates cleanup command
    subparsers.add_parser('duplicates', help='Clean up duplicate entries in shows history')
    
    # Processed articles cleanup command
    articles_parser = subparsers.add_parser('cleanup-articles', help='Clean up old processed articles')
    articles_parser.add_argument('--max', type=int, default=100, help='Maximum number of articles to keep')
    
    # Reset command
    subparsers.add_parser('reset', help='Reset all storage data')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize storage
    storage = ShowDataStorage(data_dir=args.data_dir)
    
    # Execute command
    if args.command == 'stats':
        show_stats(storage)
    elif args.command == 'history':
        show_history(storage, args.limit)
    elif args.command == 'search':
        search_shows(storage, args.query)
    elif args.command == 'platform':
        filter_by_platform(storage, args.name)
    elif args.command == 'cleanup':
        cleanup_data(storage, args.days)
    elif args.command == 'duplicates':
        cleanup_duplicates(storage)
    elif args.command == 'cleanup-articles':
        cleanup_processed_articles(storage, args.max)
    elif args.command == 'reset':
        reset_storage(storage)

if __name__ == "__main__":
    main()
