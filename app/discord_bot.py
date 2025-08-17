"""
Discord integration module for Guardian Seven Best Shows Monitor.
Sends formatted notifications about new show recommendations to Discord.
"""

from discord_webhook import DiscordEmbed, DiscordWebhook
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GuardianDiscordBot:
    """Discord bot for sending Guardian Seven Best Shows notifications."""
    
    def __init__(self, env_path: str = None):
        """
        Initialize Discord bot with webhook configuration.
        
        Args:
            env_path: Path to .env file. Defaults to project root.
        """
        # Load environment variables
        if env_path:
            load_dotenv(env_path)
        else:
            # Try to load from project root
            env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
            if os.path.exists(env_file):
                load_dotenv(env_file)
            else:
                load_dotenv()  # Load from system environment
        
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        
        if not self.webhook_url:
            logger.warning("DISCORD_WEBHOOK_URL not found in environment variables")
        else:
            logger.info("Discord webhook configured successfully")
    
    def send_new_shows_alert(self, article_title: str, article_date: str, 
                           article_url: str, shows: List[Dict[str, str]]) -> bool:
        """
        Send notification about new Guardian show recommendations.
        
        Args:
            article_title: Title of the Guardian article
            article_date: Publication date (YYYY-MM-DD)
            article_url: URL of the article
            shows: List of show dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        if not self.webhook_url:
            logger.error("Cannot send Discord notification: webhook URL not configured")
            return False
        
        try:
            # Create main embed
            embed = DiscordEmbed(
                title="🎬 New Guardian Show Recommendations!",
                description=f"**{len(shows)} new shows** to stream this week from The Guardian",
                color=0x052962,  # Guardian blue color
                url=article_url
            )
            
            # Add article info
            embed.add_embed_field(
                name="📅 Published", 
                value=self._format_date(article_date), 
                inline=True
            )
            embed.add_embed_field(
                name="📰 Source", 
                value="The Guardian", 
                inline=True
            )
            embed.add_embed_field(
                name="🔗 Read Full Article", 
                value=f"[Click Here]({article_url})", 
                inline=False
            )
            
            # Add shows (limit to prevent embed from being too long)
            shows_to_display = shows[:7]  # Guardian typically has 7 shows
            
            for i, show in enumerate(shows_to_display, 1):
                title = show.get('title', 'Unknown Show')
                platform = show.get('platform', 'Platform not specified')
                description = show.get('description', 'No description available')
                pick_of_the_week = show.get('pick_of_the_week', False)
                
                # Add "Pick of the week" indicator to title if applicable
                display_title = title
                if pick_of_the_week:
                    display_title = f"⭐ {title} (Pick of the week)"
                
                # Truncate description if too long
                if len(description) > 150:
                    description = description[:147] + "..."
                
                # Format show entry
                show_text = f"**Platform:** {platform}\n{description}"
                
                embed.add_embed_field(
                    name=f"{i}. {display_title}",
                    value=show_text,
                    inline=False
                )
            
            # Add footer
            embed.set_footer(
                text="Guardian Seven Best Shows Monitor",
                icon_url="https://assets.guim.co.uk/images/favicons/fee5e2d638d1c35f6d501fa397e53329/152x152.png"
            )
            
            # Set timestamp
            embed.set_timestamp()
            
            # Send webhook
            webhook = DiscordWebhook(url=self.webhook_url)
            webhook.add_embed(embed)
            response = webhook.execute()
            
            if response.status_code == 200:
                logger.info(f"Discord notification sent successfully for {len(shows)} shows")
                return True
            else:
                logger.error(f"Failed to send Discord notification. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")
            return False
    
    def send_error_notification(self, error_message: str, context: str = None) -> bool:
        """
        Send error notification to Discord.
        
        Args:
            error_message: Description of the error
            context: Additional context about when/where the error occurred
            
        Returns:
            True if successful, False otherwise
        """
        if not self.webhook_url:
            logger.error("Cannot send Discord notification: webhook URL not configured")
            return False
        
        try:
            embed = DiscordEmbed(
                title="⚠️ Guardian Monitor Error",
                description="An error occurred while monitoring Guardian show recommendations",
                color=0xff0000  # Red color for errors
            )
            
            embed.add_embed_field(
                name="Error Message",
                value=error_message,
                inline=False
            )
            
            if context:
                embed.add_embed_field(
                    name="Context",
                    value=context,
                    inline=False
                )
            
            embed.add_embed_field(
                name="Timestamp",
                value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                inline=True
            )
            
            embed.set_footer(text="Guardian Seven Best Shows Monitor - Error Alert")
            
            # Send webhook
            webhook = DiscordWebhook(url=self.webhook_url)
            webhook.add_embed(embed)
            response = webhook.execute()
            
            if response.status_code == 200:
                logger.info("Error notification sent successfully")
                return True
            else:
                logger.error(f"Failed to send error notification. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
            return False
    
    def send_test_message(self) -> bool:
        """
        Send a test message to verify Discord integration.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.webhook_url:
            logger.error("Cannot send test message: webhook URL not configured")
            return False
        
        try:
            embed = DiscordEmbed(
                title="🧪 Test Message",
                description="Guardian Seven Best Shows Monitor is working correctly!",
                color=0x00ff00  # Green color
            )
            
            embed.add_embed_field(
                name="Status",
                value="✅ All systems operational",
                inline=True
            )
            
            embed.add_embed_field(
                name="Test Time",
                value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                inline=True
            )
            
            embed.set_footer(text="Guardian Seven Best Shows Monitor - Test")
            
            # Send webhook
            webhook = DiscordWebhook(url=self.webhook_url)
            webhook.add_embed(embed)
            response = webhook.execute()
            
            if response.status_code == 200:
                logger.info("Test message sent successfully")
                return True
            else:
                logger.error(f"Failed to send test message. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending test message: {e}")
            return False
    
    def _format_date(self, date_str: str) -> str:
        """
        Format date string for display.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            Formatted date string
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%B %d, %Y")
        except ValueError:
            return date_str  # Return original if parsing fails
    
    def is_configured(self) -> bool:
        """
        Check if Discord webhook is properly configured.
        
        Returns:
            True if webhook URL is available, False otherwise
        """
        return bool(self.webhook_url)


def main():
    """Test the Discord bot functionality."""
    bot = GuardianDiscordBot()
    
    if not bot.is_configured():
        print("❌ Discord webhook not configured. Please set DISCORD_WEBHOOK_URL environment variable.")
        print("Example: export DISCORD_WEBHOOK_URL='https://discord.com/api/webhooks/...'")
        return
    
    print("🧪 Testing Discord integration...")
    
    # Test basic connectivity
    if bot.send_test_message():
        print("✅ Test message sent successfully")
    else:
        print("❌ Failed to send test message")
        return
    
    # Test with sample show data
    sample_shows = [
        {
            'title': 'Sample Show 1',
            'description': 'A thrilling drama about testing Discord notifications with sample data.',
            'platform': 'Netflix',
            'pick_of_the_week': True
        },
        {
            'title': 'Sample Show 2',
            'description': 'An exciting comedy series that demonstrates the notification system.',
            'platform': 'Disney+',
            'pick_of_the_week': False
        },
        {
            'title': 'Sample Show 3',
            'description': 'A documentary about the importance of proper testing in software development.',
            'platform': 'Apple TV+',
            'pick_of_the_week': False
        }
    ]
    
    # Test new shows alert
    success = bot.send_new_shows_alert(
        article_title="Test Article - Seven Best Shows to Stream This Week",
        article_date="2025-08-17",
        article_url="https://example.com/test-article",
        shows=sample_shows
    )
    
    if success:
        print("✅ New shows alert sent successfully")
    else:
        print("❌ Failed to send new shows alert")
    
    print("🎉 Discord integration test completed!")


if __name__ == "__main__":
    main()
