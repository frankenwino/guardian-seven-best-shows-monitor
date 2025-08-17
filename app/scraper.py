"""
Web scraper module for The Guardian's "Seven Best Shows to Stream This Week" series.
Handles fetching series index, finding latest articles, and parsing show recommendations.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
import logging
from typing import List, Dict, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GuardianScraper:
    """Scraper for The Guardian's Seven Best Shows series."""
    
    def __init__(self):
        self.base_url = "https://www.theguardian.com"
        self.series_url = "https://www.theguardian.com/tv-and-radio/series/the-seven-best-shows-to-stream-this-week"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch a web page and return BeautifulSoup object.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing {url}: {e}")
            return None
    
    def get_series_articles(self) -> List[Dict[str, str]]:
        """
        Get all articles from the series index page.
        
        Returns:
            List of dictionaries with article info (url, title, date)
        """
        soup = self.fetch_page(self.series_url)
        if not soup:
            return []
        
        articles = []
        
        # Look for article links in the series page
        # Guardian typically uses specific CSS classes for article listings
        article_links = soup.find_all('a', href=True)
        
        for link in article_links:
            href = link.get('href')
            if not href:
                continue
                
            # Check if this is a "seven best shows" article
            if self._is_seven_best_shows_article(href):
                full_url = urljoin(self.base_url, href)
                title = self._extract_title_from_link(link)
                date = self._extract_date_from_url(href)
                
                # If we can't extract title from link, generate one from URL
                if not title and date:
                    title = f"Seven Best Shows to Stream This Week - {date}"
                
                if date:  # Only add if we have a date
                    articles.append({
                        'url': full_url,
                        'title': title.strip() if title else f"Seven Best Shows - {date}",
                        'date': date,
                        'path': href
                    })
        
        # Sort by date (newest first)
        articles.sort(key=lambda x: x['date'], reverse=True)
        
        logger.info(f"Found {len(articles)} articles in series")
        return articles
    
    def _is_seven_best_shows_article(self, href: str) -> bool:
        """Check if URL is a seven best shows article."""
        if not href:
            return False
            
        # Pattern matching for Guardian seven best shows URLs
        patterns = [
            r'/tv-and-radio/\d{4}/\w{3}/\d{2}/.+seven-best-shows',
            r'/tv-and-radio/\d{4}/\w{3}/\d{2}/.+best-shows-to-stream',
        ]
        
        for pattern in patterns:
            if re.search(pattern, href):
                return True
        
        # Also check for "seven-best" or "best-shows" in the URL
        if 'seven-best' in href.lower() or 'best-shows-to-stream' in href.lower():
            # Make sure it's not just the series page itself and has a date pattern
            if '/series/' not in href and re.search(r'/\d{4}/', href):
                return True
        
        return False
    
    def _extract_title_from_link(self, link_element) -> Optional[str]:
        """Extract article title from link element."""
        # Try different methods to get the title
        title = link_element.get_text(strip=True)
        
        if not title:
            # Look for title in nested elements
            title_elem = link_element.find(['h3', 'h2', 'span'])
            if title_elem:
                title = title_elem.get_text(strip=True)
        
        return title if title else None
    
    def _extract_date_from_url(self, url: str) -> Optional[str]:
        """Extract date from Guardian URL pattern."""
        # Guardian URLs typically have format: /YYYY/MMM/DD/
        date_pattern = r'/(\d{4})/(\w{3})/(\d{2})/'
        match = re.search(date_pattern, url)
        
        if match:
            year, month_abbr, day = match.groups()
            try:
                # Convert month abbreviation to number
                month_map = {
                    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                    'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                    'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                }
                month = month_map.get(month_abbr.lower(), '01')
                return f"{year}-{month}-{day}"
            except Exception:
                pass
        
        return None
    
    def get_latest_article_url(self, last_checked_url: Optional[str] = None) -> Optional[str]:
        """
        Get the latest article URL that hasn't been checked yet.
        
        Args:
            last_checked_url: URL of the last article that was processed
            
        Returns:
            URL of the latest unchecked article or None
        """
        articles = self.get_series_articles()
        
        if not articles:
            logger.warning("No articles found in series")
            return None
        
        # If no last checked URL, return the latest article
        if not last_checked_url:
            return articles[0]['url']
        
        # Find articles newer than the last checked one
        for article in articles:
            if article['url'] == last_checked_url:
                break
            # Return the first (newest) article that's different from last checked
            return article['url']
        
        # If we get here, no new articles found
        logger.info("No new articles found since last check")
        return None
    
    def parse_show_recommendations(self, article_url: str) -> List[Dict[str, str]]:
        """
        Parse TV show recommendations from a Guardian article.
        
        Args:
            article_url: URL of the article to parse
            
        Returns:
            List of show dictionaries with title, description, platform
        """
        soup = self.fetch_page(article_url)
        if not soup:
            return []
        
        shows = []
        
        # Find the article content area
        article_content = soup.find('div', {'data-gu-name': 'body'}) or soup.find('div', class_=lambda x: x and 'article-body' in x)
        
        if not article_content:
            # Fallback to searching the entire page
            article_content = soup
        
        # Guardian articles use h2 headings for each show
        headings = article_content.find_all('h2')
        
        for heading in headings:
            show_data = self._parse_show_from_guardian_heading(heading)
            if show_data:
                shows.append(show_data)
        
        # If no shows found with h2, try other methods
        if not shows:
            # Method 2: Look for numbered headings (h2, h3)
            headings = soup.find_all(['h2', 'h3'], string=re.compile(r'^\d+\.'))
            
            for heading in headings:
                show_data = self._parse_show_from_heading(heading)
                if show_data:
                    shows.append(show_data)
        
        # Method 3: Look for strong/bold text with numbers
        if not shows:
            numbered_elements = soup.find_all(['strong', 'b'], string=re.compile(r'^\d+\.'))
            for element in numbered_elements:
                show_data = self._parse_show_from_element(element)
                if show_data:
                    shows.append(show_data)
        
        # Method 4: Look for article body and parse sequentially
        if not shows:
            shows = self._parse_shows_from_body(soup)
        
        logger.info(f"Parsed {len(shows)} shows from {article_url}")
        return shows  # Return all shows found
    
    def _parse_show_from_guardian_heading(self, heading) -> Optional[Dict[str, str]]:
        """Parse show data from Guardian's h2 heading structure."""
        title_text = heading.get_text(strip=True)
        
        # Skip headings that are clearly not show titles
        skip_patterns = [
            r'^pick of the week$',
            r'^privacy notice',
            r'^related:',
            r'^more on this story',
            r'^advertisement',
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, title_text.lower()):
                return None
        
        # Check if this is the "Pick of the week" show
        pick_of_the_week = False
        show_title = title_text
        
        # Handle "Pick of the week" prefix
        if title_text.lower().startswith('pick of the week'):
            pick_of_the_week = True
            # Remove the prefix and clean up the title
            show_title = re.sub(r'^pick of the week\s*', '', title_text, flags=re.IGNORECASE).strip()
        
        # Look for description in following paragraphs
        description_parts = []
        platform = ""
        
        # Find next siblings for description
        current = heading.next_sibling
        paragraph_count = 0
        
        while current and paragraph_count < 3:  # Limit to avoid getting too much
            if hasattr(current, 'name'):
                if current.name == 'p':
                    text = current.get_text(strip=True)
                    if text and not text.startswith(('http', 'www', 'Related:', 'More on this story')):
                        description_parts.append(text)
                        paragraph_count += 1
                elif current.name in ['h1', 'h2', 'h3'] and current != heading:
                    break  # Stop at next heading
            current = current.next_sibling
        
        description = ' '.join(description_parts)
        
        # Extract platform information from title and description
        platform = self._extract_platform(description + " " + show_title)
        
        # Only return if we have a meaningful title
        if len(show_title) > 2 and not show_title.lower() in ['advertisement', 'related']:
            return {
                'title': show_title,
                'description': description[:500] if description else 'No description available',
                'platform': platform,
                'pick_of_the_week': pick_of_the_week
            }
        
        return None
    
    def _parse_show_from_heading(self, heading) -> Optional[Dict[str, str]]:
        """Parse show data starting from a heading element."""
        title_text = heading.get_text(strip=True)
        
        # Extract show title (remove number prefix)
        title_match = re.match(r'^\d+\.\s*(.+)', title_text)
        if not title_match:
            return None
        
        raw_title = title_match.group(1).strip()
        
        # Check if this is the "Pick of the week" show
        pick_of_the_week = False
        show_title = raw_title
        
        # Handle "Pick of the week" prefix
        if raw_title.lower().startswith('pick of the week'):
            pick_of_the_week = True
            # Remove the prefix and clean up the title
            show_title = re.sub(r'^pick of the week\s*', '', raw_title, flags=re.IGNORECASE).strip()
        
        # Look for description in following paragraphs
        description = ""
        platform = ""
        
        # Find next siblings for description
        current = heading.next_sibling
        description_parts = []
        
        while current and len(description_parts) < 3:  # Limit to avoid getting too much
            if hasattr(current, 'name'):
                if current.name in ['p']:
                    text = current.get_text(strip=True)
                    if text and not text.startswith(('http', 'www')):
                        description_parts.append(text)
                elif current.name in ['h1', 'h2', 'h3'] and current != heading:
                    break  # Stop at next heading
            current = current.next_sibling
        
        description = ' '.join(description_parts)
        
        # Extract platform information
        platform = self._extract_platform(description + " " + show_title)
        
        return {
            'title': show_title,
            'description': description[:500],  # Limit description length
            'platform': platform,
            'pick_of_the_week': pick_of_the_week
        }
    
    def _parse_show_from_element(self, element) -> Optional[Dict[str, str]]:
        """Parse show data starting from a bold/strong element."""
        title_text = element.get_text(strip=True)
        
        # Extract show title
        title_match = re.match(r'^\d+\.\s*(.+)', title_text)
        if not title_match:
            return None
        
        raw_title = title_match.group(1).strip()
        
        # Check if this is the "Pick of the week" show
        pick_of_the_week = False
        show_title = raw_title
        
        # Handle "Pick of the week" prefix
        if raw_title.lower().startswith('pick of the week'):
            pick_of_the_week = True
            # Remove the prefix and clean up the title
            show_title = re.sub(r'^pick of the week\s*', '', raw_title, flags=re.IGNORECASE).strip()
        
        # Look for description in parent paragraph or following text
        description = ""
        parent = element.parent
        
        if parent:
            # Get text from parent, excluding the title part
            full_text = parent.get_text(strip=True)
            if title_text in full_text:
                description = full_text.replace(title_text, '').strip()
        
        platform = self._extract_platform(description + " " + show_title)
        
        return {
            'title': show_title,
            'description': description[:500],
            'platform': platform,
            'pick_of_the_week': pick_of_the_week
        }
    
    def _parse_shows_from_body(self, soup) -> List[Dict[str, str]]:
        """Fallback method to parse shows from article body."""
        shows = []
        
        # Look for the main article content
        article_body = soup.find(['div'], class_=re.compile(r'article|content|body'))
        
        if not article_body:
            # Fallback to looking in the entire page
            article_body = soup
        
        # Find all text that might be show titles (numbered items)
        text_content = article_body.get_text()
        
        # Split by common patterns and look for numbered items
        lines = text_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+\.\s+', line):
                # This looks like a numbered show
                title_match = re.match(r'^\d+\.\s*(.+)', line)
                if title_match:
                    raw_title = title_match.group(1).strip()
                    
                    # Check if this is the "Pick of the week" show
                    pick_of_the_week = False
                    show_title = raw_title
                    
                    # Handle "Pick of the week" prefix
                    if raw_title.lower().startswith('pick of the week'):
                        pick_of_the_week = True
                        # Remove the prefix and clean up the title
                        show_title = re.sub(r'^pick of the week\s*', '', raw_title, flags=re.IGNORECASE).strip()
                    
                    # For fallback method, we have limited description
                    shows.append({
                        'title': show_title,
                        'description': 'Description not available',
                        'platform': self._extract_platform(show_title),
                        'pick_of_the_week': pick_of_the_week
                    })
        
        return shows
    
    def _extract_platform(self, text: str) -> str:
        """Extract streaming platform from text."""
        if not text:
            return "Platform not specified"
        
        text_lower = text.lower()
        
        # Common streaming platforms
        platforms = {
            'netflix': 'Netflix',
            'amazon prime': 'Amazon Prime Video',
            'prime video': 'Amazon Prime Video',
            'disney+': 'Disney+',
            'disney plus': 'Disney+',
            'hbo max': 'HBO Max',
            'hbo': 'HBO',
            'hulu': 'Hulu',
            'apple tv': 'Apple TV+',
            'paramount+': 'Paramount+',
            'peacock': 'Peacock',
            'bbc iplayer': 'BBC iPlayer',
            'itv hub': 'ITV Hub',
            'all 4': 'All 4',
            'channel 4': 'All 4',
            'sky': 'Sky',
            'now tv': 'NOW TV',
            'britbox': 'BritBox',
            'youtube': 'YouTube',
            'crunchyroll': 'Crunchyroll'
        }
        
        for key, platform in platforms.items():
            if key in text_lower:
                return platform
        
        return "Platform not specified"


def main():
    """Test the scraper functionality."""
    scraper = GuardianScraper()
    
    # Test getting series articles
    print("Fetching series articles...")
    articles = scraper.get_series_articles()
    
    if articles:
        print(f"Found {len(articles)} articles:")
        for i, article in enumerate(articles[:3]):  # Show first 3
            print(f"{i+1}. {article['title']} ({article['date']})")
            print(f"   URL: {article['url']}")
        
        # Test parsing the latest article
        latest_url = articles[0]['url']
        print(f"\nParsing shows from latest article: {latest_url}")
        shows = scraper.parse_show_recommendations(latest_url)
        
        if shows:
            print(f"Found {len(shows)} shows:")
            for i, show in enumerate(shows, 1):
                print(f"{i}. {show['title']}")
                print(f"   Platform: {show['platform']}")
                print(f"   Description: {show['description'][:100]}...")
                print()
        else:
            print("No shows found in the article")
    else:
        print("No articles found")


if __name__ == "__main__":
    main()
