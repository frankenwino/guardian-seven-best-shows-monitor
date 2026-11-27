"""
Web scraper module for The Guardian's show and film recommendation series.
Fetches article listings and body content via the Guardian Content API.
Parses individual show/film recommendations from article HTML.
"""

import os
import re
import logging
from typing import List, Dict, Optional, Any

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Guardian Content API base URL
GUARDIAN_API_URL = "https://content.guardianapis.com/search"
GUARDIAN_BASE_URL = "https://www.theguardian.com"


class GuardianScraper:
    """Fetches and parses Guardian show/film recommendation articles."""

    def __init__(
        self,
        series_urls: Optional[List[str]] = None,
        timeout: int = 10,
        user_agent: Optional[str] = None,
        retry_attempts: int = 3,
        retry_delay: int = 5,
    ):
        """
        Initialise the scraper.

        Args:
            series_urls: Guardian series page URLs to monitor. Each URL is converted
                         to a Guardian Content API tag for fetching. Defaults to the
                         weekly "Seven Best Shows" series.
            timeout:     HTTP request timeout in seconds.
            user_agent:  Override the default User-Agent header.
            retry_attempts: Number of times to retry a failed page fetch.
            retry_delay:    Seconds to wait between fetch retries.
        """
        self.series_urls = series_urls or [
            f"{GUARDIAN_BASE_URL}/tv-and-radio/series/the-seven-best-shows-to-stream-this-week"
        ]
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.headers = {
            "User-Agent": user_agent or (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    # ── Tag helpers ───────────────────────────────────────────────────────────

    def _series_url_to_tag(self, url: str) -> str:
        """Convert a Guardian series page URL to a Content API tag path.

        Example:
            'https://www.theguardian.com/film/series/best-films-of-2025'
            → 'film/series/best-films-of-2025'
        """
        return url.replace(f"{GUARDIAN_BASE_URL}/", "").strip("/")

    def _series_type_from_tag(self, tag: str) -> str:
        """Classify an API tag as 'weekly', 'annual_tv', or 'annual_film'.

        Returns:
            'annual_film' if the tag is under the film section.
            'annual_tv'   if the tag matches a year-in-TV or best-TV-of-year pattern.
            'weekly'      otherwise.
        """
        if tag.startswith("film/"):
            return "annual_film"
        if re.search(r"\d{4}-in-tv", tag) or re.search(r"best-tv-of-\d{4}", tag):
            return "annual_tv"
        return "weekly"

    # ── Article fetching ──────────────────────────────────────────────────────

    def get_series_articles(self) -> List[Dict[str, str]]:
        """Fetch articles from all configured series via the Guardian Content API.

        Each series URL is converted to an API tag. The API is called once per tag
        and results are merged. Each returned article dict includes 'series_tag' and
        'series_type' so callers can route behaviour per article.

        Returns:
            List of article dicts with keys:
                url, title, date, path, body_html, series_tag, series_type
        """
        api_key = os.getenv("GUARDIAN_API_KEY")
        if not api_key:
            logger.error("GUARDIAN_API_KEY not set — cannot fetch series articles")
            return []

        all_articles: List[Dict[str, str]] = []

        for series_url in self.series_urls:
            tag = self._series_url_to_tag(series_url)
            series_type = self._series_type_from_tag(tag)
            articles = self._fetch_articles_for_tag(tag, series_type, api_key)
            all_articles.extend(articles)

        logger.info(f"Found {len(all_articles)} articles across all series")
        return all_articles

    def _fetch_articles_for_tag(
        self, tag: str, series_type: str, api_key: str
    ) -> List[Dict[str, str]]:
        """Fetch articles for a single Guardian API tag.

        Args:
            tag:         Guardian Content API tag path.
            series_type: 'weekly', 'annual_tv', or 'annual_film'.
            api_key:     Guardian Content API key.

        Returns:
            List of article dicts, or empty list on error.
        """
        try:
            resp = requests.get(
                GUARDIAN_API_URL,
                params={
                    "tag": tag,
                    "api-key": api_key,
                    "show-fields": "headline,trailText,body",
                    "order-by": "newest",
                    "page-size": 50,
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
            results = resp.json()["response"]["results"]
        except Exception as exc:
            logger.error(f"Guardian API request failed for tag '{tag}': {exc}")
            return []

        articles = []
        for r in results:
            date = self._extract_date_from_url(r["webUrl"])
            articles.append(
                {
                    "url": r["webUrl"],
                    "title": r["webTitle"],
                    "date": date or "",
                    "path": r["id"],
                    "body_html": r.get("fields", {}).get("body", ""),
                    "series_tag": tag,
                    "series_type": series_type,
                }
            )

        logger.info(f"Fetched {len(articles)} articles for tag '{tag}'")
        return articles

    # ── Page fetching (fallback for parse_show_recommendations) ───────────────

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a web page and return a BeautifulSoup object.

        Used as a fallback when body_html is not available. Retries up to
        retry_attempts times with retry_delay seconds between attempts.
        """
        import time

        for attempt in range(1, self.retry_attempts + 1):
            try:
                logger.info(f"Fetching: {url} (attempt {attempt}/{self.retry_attempts})")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return BeautifulSoup(response.content, "html.parser")
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt} failed for {url}: {e}")
                if attempt < self.retry_attempts:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"All {self.retry_attempts} attempts failed for {url}")
            except Exception as e:
                logger.error(f"Unexpected error parsing {url}: {e}")
                return None

        return None

    # ── Show parsing ──────────────────────────────────────────────────────────

    def parse_show_recommendations(
        self, article_url: str, body_html: str = ""
    ) -> List[Dict[str, Any]]:
        """Parse show/film recommendations from a Guardian article.

        When body_html is supplied (as returned by the Content API), it is parsed
        directly — no additional HTTP request is made. Falls back to fetching the
        page via fetch_page if body_html is empty.

        Args:
            article_url: URL of the article (used for fetch_page fallback and logging).
            body_html:   Pre-fetched HTML body from the Guardian API.

        Returns:
            List of show dicts with keys: title, description, platform, pick_of_the_week.
        """
        if body_html:
            soup = BeautifulSoup(body_html, "html.parser")
        else:
            soup = self.fetch_page(article_url)
        if not soup:
            return []

        shows = []

        # Find the article body element
        article_content = (
            soup.find("div", {"data-gu-name": "body"})
            or soup.find("div", class_=lambda x: x and "article-body" in x)
            or soup
        )

        # Method 1: h2 headings (normal Guardian format)
        headings = article_content.find_all("h2")
        for heading in headings:
            show_data = self._parse_show_from_guardian_heading(heading)
            if show_data:
                shows.append(show_data)

        # Method 2: numbered h2/h3 headings
        if not shows:
            headings = article_content.find_all(
                re.compile(r"^h[23]$"), string=re.compile(r"^\d+\.")  # type: ignore[call-overload]
            )
            for heading in headings:
                show_data = self._parse_show_from_heading(heading)
                if show_data:
                    shows.append(show_data)

        # Method 3: bold/strong numbered elements
        if not shows:
            numbered = soup.find_all(
                re.compile(r"^(strong|b)$"), string=re.compile(r"^\d+\.")  # type: ignore[call-overload]
            )
            for element in numbered:
                show_data = self._parse_show_from_element(element)
                if show_data:
                    shows.append(show_data)

        # Method 4: raw body text scan
        if not shows:
            shows = self._parse_shows_from_body(soup)

        logger.info(f"Parsed {len(shows)} shows from {article_url}")
        return shows

    def _parse_show_from_guardian_heading(
        self, heading
    ) -> Optional[Dict[str, Any]]:
        """Parse a show from a Guardian h2 heading and its following paragraphs."""
        title_text = heading.get_text(strip=True)

        skip_patterns = [
            r"^pick of the week$",
            r"^privacy notice",
            r"^related:",
            r"^more on this story",
            r"^advertisement",
        ]
        for pattern in skip_patterns:
            if re.match(pattern, title_text.lower()):
                return None

        pick_of_the_week = False
        show_title = title_text
        if title_text.lower().startswith("pick of the week"):
            pick_of_the_week = True
            show_title = re.sub(
                r"^pick of the week\s*", "", title_text, flags=re.IGNORECASE
            ).strip()

        description_parts = []
        current = heading.next_sibling
        paragraph_count = 0
        while current and paragraph_count < 3:
            if hasattr(current, "name"):
                if current.name == "p":
                    text = current.get_text(strip=True)
                    if text and not text.startswith(
                        ("http", "www", "Related:", "More on this story")
                    ):
                        description_parts.append(text)
                        paragraph_count += 1
                elif current.name in ["h1", "h2", "h3"] and current != heading:
                    break
            current = current.next_sibling

        description = " ".join(description_parts)
        platform = self._extract_platform(description + " " + show_title)

        if len(show_title) > 2 and show_title.lower() not in ["advertisement", "related"]:
            return {
                "title": show_title,
                "description": description[:500] if description else "No description available",
                "platform": platform,
                "pick_of_the_week": pick_of_the_week,
            }
        return None

    def _parse_show_from_heading(self, heading) -> Optional[Dict[str, Any]]:
        """Parse a show from a numbered h2/h3 heading."""
        title_text = heading.get_text(strip=True)
        title_match = re.match(r"^\d+\.\s*(.+)", title_text)
        if not title_match:
            return None

        raw_title = title_match.group(1).strip()
        pick_of_the_week = False
        show_title = raw_title
        if raw_title.lower().startswith("pick of the week"):
            pick_of_the_week = True
            show_title = re.sub(
                r"^pick of the week\s*", "", raw_title, flags=re.IGNORECASE
            ).strip()

        current = heading.next_sibling
        description_parts: List[str] = []
        while current and len(description_parts) < 3:
            if hasattr(current, "name"):
                if current.name == "p":
                    text = current.get_text(strip=True)
                    if text and not text.startswith(("http", "www")):
                        description_parts.append(text)
                elif current.name in ["h1", "h2", "h3"] and current != heading:
                    break
            current = current.next_sibling

        description = " ".join(description_parts)
        platform = self._extract_platform(description + " " + show_title)

        return {
            "title": show_title,
            "description": description[:500],
            "platform": platform,
            "pick_of_the_week": pick_of_the_week,
        }

    def _parse_show_from_element(self, element) -> Optional[Dict[str, Any]]:
        """Parse a show from a bold/strong numbered element."""
        title_text = element.get_text(strip=True)
        title_match = re.match(r"^\d+\.\s*(.+)", title_text)
        if not title_match:
            return None

        raw_title = title_match.group(1).strip()
        pick_of_the_week = False
        show_title = raw_title
        if raw_title.lower().startswith("pick of the week"):
            pick_of_the_week = True
            show_title = re.sub(
                r"^pick of the week\s*", "", raw_title, flags=re.IGNORECASE
            ).strip()

        description = ""
        parent = element.parent
        if parent:
            full_text = parent.get_text(strip=True)
            if title_text in full_text:
                description = full_text.replace(title_text, "").strip()

        platform = self._extract_platform(description + " " + show_title)
        return {
            "title": show_title,
            "description": description[:500],
            "platform": platform,
            "pick_of_the_week": pick_of_the_week,
        }

    def _parse_shows_from_body(self, soup) -> List[Dict[str, Any]]:
        """Fallback: scan raw body text for numbered show entries."""
        shows = []
        article_body = (
            soup.find(["div"], class_=re.compile(r"article|content|body")) or soup
        )
        lines = article_body.get_text().split("\n")
        for line in lines:
            line = line.strip()
            if re.match(r"^\d+\.\s+", line):
                title_match = re.match(r"^\d+\.\s*(.+)", line)
                if title_match:
                    raw_title = title_match.group(1).strip()
                    pick_of_the_week = False
                    show_title = raw_title
                    if raw_title.lower().startswith("pick of the week"):
                        pick_of_the_week = True
                        show_title = re.sub(
                            r"^pick of the week\s*", "", raw_title, flags=re.IGNORECASE
                        ).strip()
                    shows.append(
                        {
                            "title": show_title,
                            "description": "Description not available",
                            "platform": self._extract_platform(show_title),
                            "pick_of_the_week": pick_of_the_week,
                        }
                    )
        return shows

    # ── Utility helpers ───────────────────────────────────────────────────────

    def _extract_date_from_url(self, url: str) -> Optional[str]:
        """Extract YYYY-MM-DD date from a Guardian URL containing /YYYY/MMM/DD/ pattern."""
        match = re.search(r"/(\d{4})/(\w{3})/(\d{2})/", url)
        if match:
            year, month_abbr, day = match.groups()
            month_map = {
                "jan": "01", "feb": "02", "mar": "03", "apr": "04",
                "may": "05", "jun": "06", "jul": "07", "aug": "08",
                "sep": "09", "oct": "10", "nov": "11", "dec": "12",
            }
            month = month_map.get(month_abbr.lower(), "01")
            return f"{year}-{month}-{day}"
        return None

    def _extract_platform(self, text: str) -> str:
        """Extract a streaming platform name from article text."""
        if not text:
            return "Platform not specified"
        text_lower = text.lower()
        platforms = {
            "netflix": "Netflix",
            "amazon prime": "Amazon Prime Video",
            "prime video": "Amazon Prime Video",
            "disney+": "Disney+",
            "disney plus": "Disney+",
            "hbo max": "HBO Max",
            "hbo": "HBO",
            "hulu": "Hulu",
            "apple tv": "Apple TV+",
            "paramount+": "Paramount+",
            "peacock": "Peacock",
            "bbc iplayer": "BBC iPlayer",
            "itv hub": "ITV Hub",
            "all 4": "All 4",
            "channel 4": "All 4",
            "sky": "Sky",
            "now tv": "NOW TV",
            "britbox": "BritBox",
            "youtube": "YouTube",
            "crunchyroll": "Crunchyroll",
        }
        for key, platform in platforms.items():
            if key in text_lower:
                return platform
        return "Platform not specified"
