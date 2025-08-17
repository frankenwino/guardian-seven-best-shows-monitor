#!/usr/bin/env python3
"""
Integration test for Guardian Seven Best Shows Monitor.
Tests the complete workflow: scraping -> storage -> Discord notification.
"""

import os
import sys
from scraper import GuardianScraper
from storage import ShowDataStorage
from discord_bot import GuardianDiscordBot

def test_complete_workflow():
    """Test the complete workflow without sending Discord notifications."""
    print("🧪 Testing Complete Workflow (without Discord)")
    print("=" * 50)
    
    # Initialize components
    scraper = GuardianScraper()
    storage = ShowDataStorage()
    discord_bot = GuardianDiscordBot()
    
    print("✅ Components initialized")
    
    # Step 1: Get articles from Guardian
    print("\n📰 Step 1: Fetching Guardian articles...")
    articles = scraper.get_series_articles()
    
    if not articles:
        print("❌ No articles found")
        return False
    
    print(f"✅ Found {len(articles)} articles")
    latest_article = articles[0]
    print(f"   Latest: {latest_article['title']} ({latest_article['date']})")
    
    # Step 2: Check if article is already processed
    print("\n💾 Step 2: Checking storage...")
    is_processed = storage.is_article_processed(latest_article['url'])
    
    if is_processed:
        print("ℹ️  Article already processed - would skip in real run")
        
        # Show what's in storage
        last_checked = storage.get_last_checked_article()
        if last_checked:
            print(f"   Last checked: {last_checked['title']}")
        
        stats = storage.get_storage_stats()
        print(f"   Storage stats: {stats['processed_articles_count']} articles, {stats['shows_history_entries']} history entries")
        
        return True
    else:
        print("✅ Article not yet processed - would process in real run")
    
    # Step 3: Parse shows from article
    print("\n🎬 Step 3: Parsing shows from article...")
    shows = scraper.parse_show_recommendations(latest_article['url'])
    
    if not shows:
        print("❌ No shows found in article")
        return False
    
    print(f"✅ Found {len(shows)} shows:")
    for i, show in enumerate(shows[:3], 1):
        print(f"   {i}. {show['title']} ({show['platform']})")
    if len(shows) > 3:
        print(f"   ... and {len(shows) - 3} more")
    
    # Step 4: Save to storage
    print("\n💾 Step 4: Saving to storage...")
    
    # Save shows data
    success = storage.save_shows_data(
        latest_article['url'],
        latest_article['title'],
        latest_article['date'],
        shows
    )
    
    if not success:
        print("❌ Failed to save shows data")
        return False
    
    # Add to processed articles
    success = storage.add_processed_article(
        latest_article['url'],
        latest_article['title'],
        latest_article['date'],
        len(shows)
    )
    
    if not success:
        print("❌ Failed to add processed article")
        return False
    
    # Update last checked
    success = storage.update_last_checked_article(
        latest_article['url'],
        latest_article['title'],
        latest_article['date']
    )
    
    if not success:
        print("❌ Failed to update last checked")
        return False
    
    print("✅ Data saved successfully")
    
    # Step 5: Test Discord notification (without sending)
    print("\n📢 Step 5: Testing Discord notification...")
    
    if discord_bot.is_configured():
        print("✅ Discord webhook is configured")
        
        # Ask user if they want to send a test notification
        response = input("   Send test Discord notification? (y/n): ").lower().strip()
        
        if response == 'y':
            success = discord_bot.send_new_shows_alert(
                latest_article['title'],
                latest_article['date'],
                latest_article['url'],
                shows
            )
            
            if success:
                print("✅ Discord notification sent successfully!")
            else:
                print("❌ Failed to send Discord notification")
        else:
            print("ℹ️  Skipped Discord notification")
    else:
        print("ℹ️  Discord webhook not configured - would skip notification")
    
    print("\n🎉 Integration test completed successfully!")
    return True

def test_storage_search():
    """Test storage search and filtering functionality."""
    print("\n🔍 Testing Storage Search & Filtering")
    print("=" * 40)
    
    storage = ShowDataStorage()
    
    # Test platform filtering
    netflix_shows = storage.get_shows_by_platform('Netflix', limit=5)
    print(f"Netflix shows: {len(netflix_shows)}")
    for show in netflix_shows[:2]:
        print(f"  - {show['title']} (from {show['article_date']})")
    
    # Test search
    search_results = storage.search_shows('show', limit=3)
    print(f"Search results for 'show': {len(search_results)}")
    for show in search_results:
        print(f"  - {show['title']} ({show['platform']})")
    
    # Show recent history
    history = storage.get_shows_history(limit=2)
    print(f"Recent history entries: {len(history)}")
    for entry in history:
        print(f"  - {entry['article_title']} ({entry['article_date']}) - {entry['shows_count']} shows")

def main():
    """Run integration tests."""
    print("🚀 Guardian Seven Best Shows Monitor - Integration Test")
    print("=" * 60)
    
    # Test complete workflow
    success = test_complete_workflow()
    
    if success:
        # Test storage functionality
        test_storage_search()
        
        print("\n" + "=" * 60)
        print("✅ All integration tests passed!")
        print("\nNext steps:")
        print("1. Set up Discord webhook URL in .env file")
        print("2. Run the main application")
        print("3. Set up scheduling (cron job) for regular checks")
    else:
        print("\n❌ Integration test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
