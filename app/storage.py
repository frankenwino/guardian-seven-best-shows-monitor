"""
Data storage module for Guardian Seven Best Shows Monitor.
Handles tracking of processed articles and storing show data using JSON files.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Set
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ShowDataStorage:
    """Handles data persistence for the Guardian Seven Best Shows Monitor."""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize storage with data directory.
        
        Args:
            data_dir: Directory to store data files. Defaults to ../data from app directory.
        """
        if data_dir is None:
            # Default to data directory at project root
            app_dir = Path(__file__).parent
            self.data_dir = app_dir.parent / "data"
        else:
            self.data_dir = Path(data_dir)
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.last_checked_file = self.data_dir / "last_checked.json"
        self.shows_history_file = self.data_dir / "shows_history.json"
        self.processed_articles_file = self.data_dir / "processed_articles.json"
        
        logger.info(f"Storage initialized with data directory: {self.data_dir}")
    
    def get_last_checked_article(self) -> Optional[Dict[str, str]]:
        """
        Get information about the last checked article.
        
        Returns:
            Dictionary with last checked article info or None if no previous check
        """
        try:
            if self.last_checked_file.exists():
                with open(self.last_checked_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Last checked article: {data.get('url', 'Unknown')}")
                    return data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading last checked file: {e}")
        
        return None
    
    def update_last_checked_article(self, article_url: str, article_title: str, 
                                  article_date: str, check_timestamp: str = None) -> bool:
        """
        Update the last checked article information.
        
        Args:
            article_url: URL of the checked article
            article_title: Title of the article
            article_date: Publication date of the article (YYYY-MM-DD)
            check_timestamp: When the check was performed (ISO format)
            
        Returns:
            True if successful, False otherwise
        """
        if check_timestamp is None:
            check_timestamp = datetime.now().isoformat()
        
        data = {
            'url': article_url,
            'title': article_title,
            'article_date': article_date,
            'checked_at': check_timestamp,
            'last_updated': check_timestamp
        }
        
        try:
            with open(self.last_checked_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Updated last checked article: {article_title}")
            return True
            
        except IOError as e:
            logger.error(f"Error writing last checked file: {e}")
            return False
    
    def is_article_processed(self, article_url: str) -> bool:
        """
        Check if an article has already been processed.
        
        Args:
            article_url: URL to check
            
        Returns:
            True if article has been processed, False otherwise
        """
        processed_articles = self.get_processed_articles()
        return article_url in processed_articles
    
    def get_processed_articles(self) -> Set[str]:
        """
        Get set of all processed article URLs.
        
        Returns:
            Set of processed article URLs
        """
        try:
            if self.processed_articles_file.exists():
                with open(self.processed_articles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('processed_urls', []))
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading processed articles file: {e}")
        
        return set()
    
    def add_processed_article(self, article_url: str, article_title: str, 
                            article_date: str, shows_count: int) -> bool:
        """
        Add an article to the processed list.
        
        Args:
            article_url: URL of the processed article
            article_title: Title of the article
            article_date: Publication date (YYYY-MM-DD)
            shows_count: Number of shows found in the article
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing data
            processed_data = {'processed_urls': [], 'articles_info': {}}
            if self.processed_articles_file.exists():
                with open(self.processed_articles_file, 'r', encoding='utf-8') as f:
                    processed_data = json.load(f)
            
            # Add new article
            if article_url not in processed_data['processed_urls']:
                processed_data['processed_urls'].append(article_url)
            
            # Store article metadata
            processed_data['articles_info'][article_url] = {
                'title': article_title,
                'date': article_date,
                'shows_count': shows_count,
                'processed_at': datetime.now().isoformat()
            }
            
            # Write back to file
            with open(self.processed_articles_file, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Added processed article: {article_title}")
            return True
            
        except IOError as e:
            logger.error(f"Error updating processed articles file: {e}")
            return False
    
    def save_shows_data(self, article_url: str, article_title: str, 
                       article_date: str, shows: List[Dict[str, str]]) -> bool:
        """
        Save show recommendations data to history.
        Only saves if this article URL is not already in the history.
        
        Args:
            article_url: URL of the source article
            article_title: Title of the article
            article_date: Publication date (YYYY-MM-DD)
            shows: List of show dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing history
            history = []
            if self.shows_history_file.exists():
                with open(self.shows_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Check if this article URL already exists in history
            for existing_entry in history:
                if existing_entry.get('article_url') == article_url:
                    logger.info(f"Article already exists in history: {article_title}")
                    return True  # Not an error, just already exists
            
            # Create new entry
            entry = {
                'article_url': article_url,
                'article_title': article_title,
                'article_date': article_date,
                'saved_at': datetime.now().isoformat(),
                'shows_count': len(shows),
                'shows': shows
            }
            
            # Add new entry at the beginning (most recent first)
            history.insert(0, entry)
            
            # Write back to file (no artificial limit - keep all history)
            with open(self.shows_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(shows)} shows from {article_title}")
            return True
            
        except IOError as e:
            logger.error(f"Error saving shows data: {e}")
            return False
    
    def get_shows_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent shows history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of show history entries
        """
        try:
            if self.shows_history_file.exists():
                with open(self.shows_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    return history[:limit]
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading shows history: {e}")
        
        return []
    
    def get_shows_by_platform(self, platform: str, limit: int = 20) -> List[Dict[str, str]]:
        """
        Get shows filtered by streaming platform from history.
        
        Args:
            platform: Platform name to filter by
            limit: Maximum number of shows to return
            
        Returns:
            List of shows from the specified platform
        """
        platform_shows = []
        history = self.get_shows_history(limit=50)  # Get more history to search through
        
        for entry in history:
            for show in entry.get('shows', []):
                if show.get('platform', '').lower() == platform.lower():
                    # Add article context to show data
                    show_with_context = show.copy()
                    show_with_context['article_date'] = entry['article_date']
                    show_with_context['article_title'] = entry['article_title']
                    platform_shows.append(show_with_context)
                    
                    if len(platform_shows) >= limit:
                        return platform_shows
        
        return platform_shows
    
    def search_shows(self, query: str, limit: int = 20) -> List[Dict[str, str]]:
        """
        Search for shows by title or description.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching shows
        """
        query_lower = query.lower()
        matching_shows = []
        history = self.get_shows_history(limit=50)
        
        for entry in history:
            for show in entry.get('shows', []):
                title = show.get('title', '').lower()
                description = show.get('description', '').lower()
                
                if query_lower in title or query_lower in description:
                    # Add article context
                    show_with_context = show.copy()
                    show_with_context['article_date'] = entry['article_date']
                    show_with_context['article_title'] = entry['article_title']
                    matching_shows.append(show_with_context)
                    
                    if len(matching_shows) >= limit:
                        return matching_shows
        
        return matching_shows
    
    def get_storage_stats(self) -> Dict[str, any]:
        """
        Get statistics about stored data.
        
        Returns:
            Dictionary with storage statistics
        """
        stats = {
            'data_directory': str(self.data_dir),
            'files_exist': {
                'last_checked': self.last_checked_file.exists(),
                'shows_history': self.shows_history_file.exists(),
                'processed_articles': self.processed_articles_file.exists()
            },
            'processed_articles_count': len(self.get_processed_articles()),
            'shows_history_entries': len(self.get_shows_history(limit=1000)),
        }
        
        # Get last checked info
        last_checked = self.get_last_checked_article()
        if last_checked:
            stats['last_checked_article'] = {
                'date': last_checked.get('article_date'),
                'title': last_checked.get('title'),
                'checked_at': last_checked.get('checked_at')
            }
        
        # Get file sizes
        for file_path in [self.last_checked_file, self.shows_history_file, self.processed_articles_file]:
            if file_path.exists():
                size_kb = file_path.stat().st_size / 1024
                stats[f'{file_path.name}_size_kb'] = round(size_kb, 2)
        
        return stats
    
    def cleanup_duplicate_history_entries(self) -> bool:
        """
        Remove duplicate entries from shows history based on article URL.
        Keeps the most recent entry for each unique article URL.
        
        Returns:
            True if cleanup was successful
        """
        try:
            if not self.shows_history_file.exists():
                logger.info("No shows history file to clean up")
                return True
            
            # Load existing history
            with open(self.shows_history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # Track seen URLs and keep only the first occurrence (most recent)
            seen_urls = set()
            cleaned_history = []
            
            for entry in history:
                article_url = entry.get('article_url')
                if article_url and article_url not in seen_urls:
                    seen_urls.add(article_url)
                    cleaned_history.append(entry)
            
            # Write back cleaned history
            with open(self.shows_history_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned_history, f, indent=2, ensure_ascii=False)
            
            removed_count = len(history) - len(cleaned_history)
            logger.info(f"Cleaned up {removed_count} duplicate history entries")
            return True
            
        except Exception as e:
            logger.error(f"Error during duplicate cleanup: {e}")
            return False
    
    def cleanup_old_data(self, keep_days: int = 90) -> bool:
        """
        Clean up old data entries (optional maintenance function).
        
        Args:
            keep_days: Number of days of data to keep
            
        Returns:
            True if cleanup was successful
        """
        try:
            cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
            
            # Clean up shows history
            if self.shows_history_file.exists():
                with open(self.shows_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                # Filter entries newer than cutoff
                filtered_history = []
                for entry in history:
                    try:
                        entry_date = datetime.fromisoformat(entry['saved_at']).timestamp()
                        if entry_date > cutoff_date:
                            filtered_history.append(entry)
                    except (ValueError, KeyError):
                        # Keep entries with invalid dates to be safe
                        filtered_history.append(entry)
                
                # Write back filtered data
                with open(self.shows_history_file, 'w', encoding='utf-8') as f:
                    json.dump(filtered_history, f, indent=2, ensure_ascii=False)
                
                removed_count = len(history) - len(filtered_history)
                logger.info(f"Cleaned up {removed_count} old history entries")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return False
        """
        Clean up old data entries (optional maintenance function).
        
        Args:
            keep_days: Number of days of data to keep
            
        Returns:
            True if cleanup was successful
        """
        try:
            cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
            
            # Clean up shows history
            if self.shows_history_file.exists():
                with open(self.shows_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                # Filter entries newer than cutoff
                filtered_history = []
                for entry in history:
                    try:
                        entry_date = datetime.fromisoformat(entry['saved_at']).timestamp()
                        if entry_date > cutoff_date:
                            filtered_history.append(entry)
                    except (ValueError, KeyError):
                        # Keep entries with invalid dates to be safe
                        filtered_history.append(entry)
                
                # Write back filtered data
                with open(self.shows_history_file, 'w', encoding='utf-8') as f:
                    json.dump(filtered_history, f, indent=2, ensure_ascii=False)
                
                removed_count = len(history) - len(filtered_history)
                logger.info(f"Cleaned up {removed_count} old history entries")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return False


def main():
    """Test the storage functionality."""
    storage = ShowDataStorage()
    
    print("=== Storage Statistics ===")
    stats = storage.get_storage_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== Testing Storage Operations ===")
    
    # Test saving sample data
    sample_shows = [
        {
            'title': 'Test Show 1',
            'description': 'A great test show about testing',
            'platform': 'Netflix'
        },
        {
            'title': 'Test Show 2', 
            'description': 'Another excellent test show',
            'platform': 'Disney+'
        }
    ]
    
    test_url = "https://example.com/test-article"
    test_title = "Test Article - Seven Best Shows"
    test_date = "2025-08-15"
    
    # Save test data
    success = storage.save_shows_data(test_url, test_title, test_date, sample_shows)
    print(f"Save shows data: {'Success' if success else 'Failed'}")
    
    # Update last checked
    success = storage.update_last_checked_article(test_url, test_title, test_date)
    print(f"Update last checked: {'Success' if success else 'Failed'}")
    
    # Add to processed articles
    success = storage.add_processed_article(test_url, test_title, test_date, len(sample_shows))
    print(f"Add processed article: {'Success' if success else 'Failed'}")
    
    # Test retrieval
    print(f"\nIs article processed: {storage.is_article_processed(test_url)}")
    
    last_checked = storage.get_last_checked_article()
    if last_checked:
        print(f"Last checked: {last_checked['title']} ({last_checked['article_date']})")
    
    # Test search
    netflix_shows = storage.get_shows_by_platform('Netflix')
    print(f"Netflix shows found: {len(netflix_shows)}")
    
    search_results = storage.search_shows('test')
    print(f"Search results for 'test': {len(search_results)}")
    
    print("\n=== Updated Storage Statistics ===")
    stats = storage.get_storage_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
