#!/usr/bin/env python3
"""
Test Discord integration with sample data.
This demonstrates what the Discord notifications will look like.
"""

from discord_bot import GuardianDiscordBot
import os

def main():
    """Test Discord bot with sample Guardian data."""
    print("🧪 Testing Discord Integration with Sample Data")
    print("=" * 50)
    
    # Initialize Discord bot
    bot = GuardianDiscordBot()
    
    if not bot.is_configured():
        print("❌ Discord webhook not configured.")
        print("\nTo test Discord integration:")
        print("1. Create a Discord webhook in your server")
        print("2. Copy the webhook URL")
        print("3. Set environment variable: export DISCORD_WEBHOOK_URL='your_webhook_url'")
        print("4. Or create a .env file with DISCORD_WEBHOOK_URL=your_webhook_url")
        return
    
    print("✅ Discord webhook configured")
    
    # Sample show data based on real Guardian content
    sample_shows = [
        {
            'title': 'Hostage',
            'description': 'Abigail Dalton has assured her husband, Alex, that becoming prime minister won\'t stop her from making their marriage work. A political thriller that explores power and personal relationships.',
            'platform': 'Netflix'
        },
        {
            'title': 'Long Story Short',
            'description': 'Exciting news for BoJack Horseman fans: creator Raphael Bob-Waksberg explores the triumphs and tragedies of life in this animated anthology series.',
            'platform': 'Netflix'
        },
        {
            'title': 'The Real Housewives of London',
            'description': 'Another bout of soul-crushing affluenza, this time introducing the London arm of a franchise that has made reality TV history.',
            'platform': 'Platform not specified'
        },
        {
            'title': 'America\'s Team: The Gambler and His Cowboys',
            'description': '"This is a soap opera, 365 days a year." Dallas Cowboys owner, president and general manager Jerry Jones built an empire.',
            'platform': 'Netflix'
        },
        {
            'title': 'The Twisted Tale of Amanda Knox',
            'description': 'This eight-part drama is written from the point of view of Amanda Knox, who was initially convicted of murdering her roommate in Italy.',
            'platform': 'Disney+'
        },
        {
            'title': 'Invasion',
            'description': 'At times during its first two seasons, this divisive sci-fi show has achieved the seemingly impossible: making an alien invasion boring.',
            'platform': 'Apple TV+'
        },
        {
            'title': 'The Truth About Jussie Smollett?',
            'description': 'The bizarre story of the allegedly racist and homophobic hate attack against actor Jussie Smollett begins to unravel.',
            'platform': 'Netflix'
        }
    ]
    
    print(f"📱 Sending notification for {len(sample_shows)} shows...")
    
    # Send main notification
    success = bot.send_new_shows_alert(
        article_title="Hostage to Long Story Short: the seven best shows to stream this week",
        article_date="2025-08-15",
        article_url="https://www.theguardian.com/tv-and-radio/2025/aug/15/hostage-to-long-story-short-the-seven-best-shows-to-stream-this-week",
        shows=sample_shows
    )
    
    if success:
        print("✅ Main notification sent successfully!")
        
        # Ask if user wants platform summary
        response = input("\nSend platform summary as well? (y/n): ").lower().strip()
        
        if response == 'y':
            success = bot.send_platform_summary(sample_shows, "2025-08-15")
            if success:
                print("✅ Platform summary sent successfully!")
            else:
                print("❌ Failed to send platform summary")
        
        # Ask if user wants to test error notification
        response = input("\nSend test error notification? (y/n): ").lower().strip()
        
        if response == 'y':
            success = bot.send_error_notification(
                "This is a test error message",
                "Testing error notification functionality"
            )
            if success:
                print("✅ Error notification sent successfully!")
            else:
                print("❌ Failed to send error notification")
    else:
        print("❌ Failed to send main notification")
    
    print("\n🎉 Discord test completed!")
    print("\nCheck your Discord channel to see the notifications!")

if __name__ == "__main__":
    main()
