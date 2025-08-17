#!/usr/bin/env python3
"""
Guardian Seven Best Shows Monitor - Main Application
Checks for new Guardian show recommendations and sends Discord notifications.
Designed to run as a single execution (e.g., via cron job).
"""

import sys
import time
import argparse
import logging
from datetime import datetime
from typing import Optional, List, Dict

from config import config
from scraper import GuardianScraper
from storage import ShowDataStorage
from discord_bot import GuardianDiscordBot

class GuardianMonitor:
    """Main application class that orchestrates all components."""
    
    def __init__(self):
        """Initialize the Guardian monitor with all components."""
        # Setup logging first
        config.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Log configuration summary
        self.logger.info("Starting Guardian Seven Best Shows Monitor")
        self.logger.info(f"Configuration: {config.get_summary()}")
        
        # Initialize components
        try:
            self.scraper = GuardianScraper()
            self.storage = ShowDataStorage(data_dir=str(config.get_data_directory_path()))
            self.discord_bot = GuardianDiscordBot() if config.is_discord_configured() else None
            
            if not self.discord_bot:
                self.logger.warning("Discord not configured - notifications will be disabled")
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    def check_for_new_shows(self) -> bool:
        """
        Check for new Guardian show recommendations and process them.
        
        Returns:
            True if new shows were found and processed, False otherwise
        """
        try:
            self.logger.info("Checking for new Guardian show recommendations...")
            
            # Get latest articles
            articles = self.scraper.get_series_articles()
            if not articles:
                self.logger.warning("No articles found in Guardian series")
                return False
            
            latest_article = articles[0]
            self.logger.info(f"Latest article: {latest_article['title']} ({latest_article['date']})")
            
            # Check if already processed
            if self.storage.is_article_processed(latest_article['url']):
                self.logger.info("Article already processed - no new content")
                return False
            
            self.logger.info("New article found - processing shows...")
            
            # Parse shows from the article
            shows = self.scraper.parse_show_recommendations(latest_article['url'])
            if not shows:
                self.logger.warning("No shows found in the article")
                return False
            
            self.logger.info(f"Found {len(shows)} shows to process")
            
            # Save to storage
            success = self._save_shows_data(latest_article, shows)
            if not success:
                self.logger.error("Failed to save shows data")
                return False
            
            # Send Discord notification
            if self.discord_bot:
                success = self._send_discord_notifications(latest_article, shows)
                if not success:
                    self.logger.error("Failed to send Discord notifications")
                    # Don't return False here - data was still processed successfully
            
            self.logger.info(f"Successfully processed {len(shows)} new shows")
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking for new shows: {e}")
            
            # Send error notification if configured
            if self.discord_bot and config.send_error_notifications:
                try:
                    self.discord_bot.send_error_notification(
                        str(e),
                        "Error occurred while checking for new Guardian show recommendations"
                    )
                except Exception as discord_error:
                    self.logger.error(f"Failed to send error notification: {discord_error}")
            
            return False
    
    def _save_shows_data(self, article: Dict[str, str], shows: List[Dict[str, str]]) -> bool:
        """
        Save shows data to storage.
        
        Args:
            article: Article information dictionary
            shows: List of show dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Save shows data
            success = self.storage.save_shows_data(
                article['url'],
                article['title'],
                article['date'],
                shows
            )
            
            if not success:
                return False
            
            # Add to processed articles
            success = self.storage.add_processed_article(
                article['url'],
                article['title'],
                article['date'],
                len(shows)
            )
            
            if not success:
                return False
            
            # Update last checked
            success = self.storage.update_last_checked_article(
                article['url'],
                article['title'],
                article['date']
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error saving shows data: {e}")
            return False
    
    def _send_discord_notifications(self, article: Dict[str, str], shows: List[Dict[str, str]]) -> bool:
        """
        Send Discord notifications for new shows.
        
        Args:
            article: Article information dictionary
            shows: List of show dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Send main notification
            success = self.discord_bot.send_new_shows_alert(
                article['title'],
                article['date'],
                article['url'],
                shows
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending Discord notifications: {e}")
            return False
    
    def run(self) -> bool:
        """
        Run a single check for new shows.
        
        Returns:
            True if new shows were found, False otherwise
        """
        self.logger.info("Running check for new shows")
        return self.check_for_new_shows()
    
    def get_status(self) -> Dict[str, any]:
        """
        Get current status of the monitor.
        
        Returns:
            Dictionary with status information
        """
        try:
            # Get storage stats
            storage_stats = self.storage.get_storage_stats()
            
            # Get last checked info
            last_checked = self.storage.get_last_checked_article()
            
            status = {
                'timestamp': datetime.now().isoformat(),
                'components': {
                    'scraper': 'initialized',
                    'storage': 'initialized',
                    'discord': 'configured' if self.discord_bot else 'not configured'
                },
                'configuration': config.get_summary(),
                'storage': {
                    'processed_articles': storage_stats['processed_articles_count'],
                    'history_entries': storage_stats['shows_history_entries'],
                    'data_directory': storage_stats['data_directory']
                }
            }
            
            if last_checked:
                status['last_checked'] = {
                    'title': last_checked['title'],
                    'date': last_checked['article_date'],
                    'checked_at': last_checked['checked_at']
                }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            return {'error': str(e)}
    
    def test_components(self) -> bool:
        """
        Test all components to ensure they're working correctly.
        
        Returns:
            True if all tests pass, False otherwise
        """
        self.logger.info("Testing all components...")
        
        try:
            # Test scraper
            self.logger.info("Testing scraper...")
            articles = self.scraper.get_series_articles()
            if not articles:
                self.logger.error("Scraper test failed - no articles found")
                return False
            self.logger.info(f"✅ Scraper test passed - found {len(articles)} articles")
            
            # Test storage
            self.logger.info("Testing storage...")
            stats = self.storage.get_storage_stats()
            self.logger.info(f"✅ Storage test passed - {stats['processed_articles_count']} processed articles")
            
            # Test Discord (if configured)
            if self.discord_bot:
                self.logger.info("Testing Discord...")
                success = self.discord_bot.send_test_message()
                if success:
                    self.logger.info("✅ Discord test passed - test message sent")
                else:
                    self.logger.error("Discord test failed - could not send test message")
                    return False
            else:
                self.logger.info("⚠️  Discord not configured - skipping test")
            
            self.logger.info("🎉 All component tests passed!")
            return True
            
        except Exception as e:
            self.logger.error(f"Component test failed: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Guardian Seven Best Shows Monitor")
    parser.add_argument('--test', action='store_true', help='Test all components')
    parser.add_argument('--status', action='store_true', help='Show current status')
    parser.add_argument('--config', action='store_true', help='Show configuration')
    
    args = parser.parse_args()
    
    try:
        # Show configuration if requested
        if args.config:
            print(config)
            return
        
        # Initialize monitor
        monitor = GuardianMonitor()
        
        # Show status if requested
        if args.status:
            status = monitor.get_status()
            print("Guardian Seven Best Shows Monitor Status:")
            print("=" * 45)
            for key, value in status.items():
                if isinstance(value, dict):
                    print(f"{key}:")
                    for sub_key, sub_value in value.items():
                        print(f"  {sub_key}: {sub_value}")
                else:
                    print(f"{key}: {value}")
            return
        
        # Test components if requested
        if args.test:
            success = monitor.test_components()
            sys.exit(0 if success else 1)
        
        # Default: run single check
        found_new = monitor.run()
        if found_new:
            print("✅ New shows found and processed")
        else:
            print("ℹ️  No new shows found")
            
    except KeyboardInterrupt:
        print("\n👋 Monitor stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
