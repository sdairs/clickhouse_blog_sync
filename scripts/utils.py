"""
Utility classes for ClickHouse blog sync system.
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import feedparser
import requests
from dateutil import parser as date_parser


class StateManager:
    """Manages sync state persistence in JSON format."""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load state from JSON file or return default state."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {self.state_file}, starting fresh")

        return {
            "last_sync": None,
            "processed_blogs": {},
            "total_blogs": 0,
            "failed_blogs": []
        }

    def save_state(self):
        """Save current state to JSON file."""
        self.state["last_sync"] = datetime.utcnow().isoformat() + "Z"
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def is_processed(self, url: str) -> bool:
        """Check if a blog URL has already been processed."""
        return url in self.state["processed_blogs"]

    def add_processed_blog(self, url: str, title: str, pub_date: str, file_path: str):
        """Add a blog to the processed list."""
        self.state["processed_blogs"][url] = {
            "title": title,
            "pub_date": pub_date,
            "file_path": file_path,
            "processed_at": datetime.utcnow().isoformat() + "Z"
        }
        self.state["total_blogs"] = len(self.state["processed_blogs"])

    def add_failed_blog(self, url: str, error: str):
        """Add a failed blog to the failed list."""
        self.state["failed_blogs"].append({
            "url": url,
            "error": error,
            "attempted_at": datetime.utcnow().isoformat() + "Z"
        })

    def get_processed_blogs(self) -> Dict[str, Dict[str, Any]]:
        """Get all processed blogs."""
        return self.state["processed_blogs"]


class SlugGenerator:
    """Generate URL-safe slugs from blog titles."""

    @staticmethod
    def generate(title: str, max_length: int = 50) -> str:
        """
        Generate a URL-safe slug from a title.

        Args:
            title: The blog title
            max_length: Maximum length of the slug

        Returns:
            A lowercase, hyphenated slug
        """
        # Convert to lowercase
        slug = title.lower()

        # Replace non-alphanumeric characters with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', slug)

        # Remove leading/trailing hyphens
        slug = slug.strip('-')

        # Truncate to max length at word boundary
        if len(slug) > max_length:
            slug = slug[:max_length]
            # Try to cut at last hyphen to avoid cutting mid-word
            last_hyphen = slug.rfind('-')
            if last_hyphen > max_length // 2:  # Only if we don't lose too much
                slug = slug[:last_hyphen]

        return slug


class RSSFetcher:
    """Fetch and parse RSS feed from ClickHouse blog."""

    RSS_URL = "https://clickhouse.com/rss.xml"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetch and parse RSS feed.

        Returns:
            List of blog entries with url, title, and pub_date
        """
        print(f"Fetching RSS feed from {self.RSS_URL}")

        try:
            response = requests.get(self.RSS_URL, timeout=self.timeout)
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            blogs = []
            for entry in feed.entries:
                # Parse publication date
                pub_date = None
                if hasattr(entry, 'published'):
                    try:
                        pub_date = date_parser.parse(entry.published).isoformat() + "Z"
                    except Exception:
                        pub_date = datetime.utcnow().isoformat() + "Z"

                blogs.append({
                    "url": entry.link,
                    "title": entry.title,
                    "pub_date": pub_date or datetime.utcnow().isoformat() + "Z"
                })

            print(f"Found {len(blogs)} blogs in RSS feed")
            return blogs

        except Exception as e:
            print(f"Error fetching RSS feed: {e}")
            raise


class MarkdownDownloader:
    """Download markdown content from ClickHouse blog posts."""

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries

    def download(self, blog_url: str) -> str:
        """
        Download markdown content by appending .md to blog URL.

        Args:
            blog_url: The blog post URL

        Returns:
            Markdown content as string
        """
        md_url = f"{blog_url}.md"

        for attempt in range(self.max_retries):
            try:
                print(f"Downloading markdown from {md_url} (attempt {attempt + 1}/{self.max_retries})")

                response = requests.get(md_url, timeout=self.timeout)
                response.raise_for_status()

                return response.text

            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [404, 403]:
                    print(f"Warning: Could not access {md_url} (status {e.response.status_code})")
                    raise
                # For other HTTP errors, retry
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Network error: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise


class FileManager:
    """Manage blog markdown files and combined file generation."""

    def __init__(self, blogs_dir: Path, combined_file: Path):
        self.blogs_dir = blogs_dir
        self.combined_file = combined_file

        # Ensure blogs directory exists
        self.blogs_dir.mkdir(parents=True, exist_ok=True)

    def generate_filename(self, pub_date: str, title: str) -> str:
        """
        Generate filename from publication date and title.

        Args:
            pub_date: ISO format date string
            title: Blog title

        Returns:
            Filename in format YYYY-MM-DD-slug.md
        """
        # Parse date and format as YYYY-MM-DD
        try:
            date_obj = date_parser.parse(pub_date)
            date_str = date_obj.strftime("%Y-%m-%d")
        except Exception:
            date_str = datetime.utcnow().strftime("%Y-%m-%d")

        # Generate slug from title
        slug = SlugGenerator.generate(title)

        return f"{date_str}-{slug}.md"

    def save_blog(self, filename: str, content: str) -> Path:
        """
        Save blog content to individual file.

        Args:
            filename: Name of the file
            content: Markdown content

        Returns:
            Path to the saved file
        """
        file_path = self.blogs_dir / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Saved blog to {file_path}")
        return file_path

    def regenerate_combined_file(self, processed_blogs: Dict[str, Dict[str, Any]]):
        """
        Regenerate the combined file with all blogs sorted newest first.

        Args:
            processed_blogs: Dictionary of processed blogs from StateManager
        """
        print("Regenerating combined file...")

        # Sort blogs by publication date (newest first)
        sorted_blogs = sorted(
            processed_blogs.items(),
            key=lambda x: x[1]["pub_date"],
            reverse=True
        )

        # Build combined content
        combined_content = []
        combined_content.append("# ClickHouse Blogs\n")
        combined_content.append(f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
        combined_content.append(f"Total blogs: {len(sorted_blogs)}\n")
        combined_content.append("\n---\n\n")

        for url, blog_info in sorted_blogs:
            file_path = Path(blog_info["file_path"])

            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Add blog to combined file with metadata header
                    combined_content.append(f"## {blog_info['title']}\n")
                    combined_content.append(f"Published: {blog_info['pub_date']}\n")
                    combined_content.append(f"URL: {url}\n\n")
                    combined_content.append(content)
                    combined_content.append("\n\n---\n\n")

                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")

        # Write combined file
        with open(self.combined_file, 'w', encoding='utf-8') as f:
            f.writelines(combined_content)

        print(f"Combined file saved to {self.combined_file}")
