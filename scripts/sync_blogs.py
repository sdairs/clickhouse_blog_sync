#!/usr/bin/env python3
"""
Main script to sync ClickHouse blogs from RSS feed.

This script:
1. Loads state from sync_state.json
2. Fetches RSS feed
3. Filters for new blogs (not in state)
4. Downloads markdown content for each new blog
5. Saves individual files to blogs/ directory
6. Regenerates all_blogs.md with all blogs sorted newest first
7. Updates and saves state
"""

import sys
from pathlib import Path

# Add scripts directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    StateManager,
    RSSFetcher,
    MarkdownDownloader,
    FileManager
)


def main():
    """Main sync orchestration."""
    # Setup paths
    project_root = Path(__file__).parent.parent
    state_file = project_root / "sync_state.json"
    blogs_dir = project_root / "blogs"
    combined_file = project_root / "all_blogs.md"

    print("=" * 60)
    print("ClickHouse Blog Sync")
    print("=" * 60)

    # Initialize components
    state_manager = StateManager(state_file)
    rss_fetcher = RSSFetcher()
    markdown_downloader = MarkdownDownloader()
    file_manager = FileManager(blogs_dir, combined_file)

    # Load current state
    print(f"\nCurrent state: {state_manager.state['total_blogs']} blogs processed")

    try:
        # Fetch RSS feed
        blogs = rss_fetcher.fetch()

        # Filter for new blogs
        new_blogs = [
            blog for blog in blogs
            if not state_manager.is_processed(blog["url"])
        ]

        print(f"\nFound {len(new_blogs)} new blogs to process")

        if not new_blogs:
            print("No new blogs to sync. Regenerating combined file...")
            file_manager.regenerate_combined_file(state_manager.get_processed_blogs())
            state_manager.save_state()
            print("\nSync complete!")
            return

        # Process each new blog
        successful_count = 0
        failed_count = 0

        for i, blog in enumerate(new_blogs, 1):
            url = blog["url"]
            title = blog["title"]
            pub_date = blog["pub_date"]

            print(f"\n[{i}/{len(new_blogs)}] Processing: {title}")
            print(f"  URL: {url}")

            try:
                # Download markdown content
                content = markdown_downloader.download(url)

                # Generate filename
                filename = file_manager.generate_filename(pub_date, title)

                # Save to individual file
                file_path = file_manager.save_blog(filename, content)

                # Update state
                state_manager.add_processed_blog(
                    url=url,
                    title=title,
                    pub_date=pub_date,
                    file_path=str(file_path.relative_to(project_root))
                )

                # Save state after each successful blog (resume on crash)
                state_manager.save_state()

                successful_count += 1
                print(f"  ✓ Success")

            except Exception as e:
                print(f"  ✗ Failed: {e}")
                state_manager.add_failed_blog(url, str(e))
                failed_count += 1
                # Continue processing remaining blogs

        # Regenerate combined file with all blogs
        print("\n" + "=" * 60)
        file_manager.regenerate_combined_file(state_manager.get_processed_blogs())

        # Save final state
        state_manager.save_state()

        # Print summary
        print("\n" + "=" * 60)
        print("Sync Summary")
        print("=" * 60)
        print(f"Total blogs in state: {state_manager.state['total_blogs']}")
        print(f"New blogs processed: {successful_count}")
        print(f"Failed blogs: {failed_count}")

        if failed_count > 0:
            print("\nFailed blogs:")
            for failed in state_manager.state["failed_blogs"][-failed_count:]:
                print(f"  - {failed['url']}: {failed['error']}")

        print("\nSync complete!")

    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
