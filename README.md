# ClickHouse Blog Sync

Automated system to sync ClickHouse blogs from RSS feed into a git repository with individual and combined markdown files.

## Features

- Fetches blogs from ClickHouse RSS feed (https://clickhouse.com/rss.xml)
- Downloads markdown content for each blog
- Saves individual blog files as `YYYY-MM-DD-slug.md`
- Generates combined file (`all_blogs.md`) with all blogs sorted newest first
- Tracks sync state to avoid reprocessing
- Automatic daily sync via GitHub Actions
- Robust error handling with per-blog retry logic
- LLM-friendly: Individual files for specific topics, combined file for comprehensive reading

## Project Structure

```
ch_blog_sync/
├── .github/workflows/
│   └── sync-blogs.yml          # GitHub Actions workflow (daily at 6 AM UTC)
├── blogs/                      # Individual blog MD files (YYYY-MM-DD-slug.md)
├── scripts/
│   ├── sync_blogs.py          # Main sync script
│   └── utils.py               # Helper functions
├── all_blogs.md               # Combined file (all blogs, newest first)
├── sync_state.json            # State tracking {processed_blogs, last_sync, errors}
├── .gitignore
├── pyproject.toml             # uv project config
└── README.md
```

## Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ch_blog_sync
```

2. Install dependencies using uv:
```bash
uv sync
```

## Usage

### Manual Sync

Run the sync script manually:

```bash
uv run python scripts/sync_blogs.py
```

The script will:
1. Load existing state from `sync_state.json`
2. Fetch the RSS feed
3. Download markdown content for new blogs
4. Save individual files to `blogs/` directory
5. Regenerate `all_blogs.md` with all blogs
6. Update `sync_state.json` with new entries

### Automatic Sync

The GitHub Actions workflow (`.github/workflows/sync-blogs.yml`) runs automatically:
- **Daily** at 6:00 AM UTC
- **Manual trigger** via GitHub Actions UI

The workflow:
1. Checks out the repository
2. Installs dependencies with uv
3. Runs the sync script
4. Commits and pushes changes if new blogs found
5. Creates a summary in the Actions UI

## State Management

The `sync_state.json` file tracks:

```json
{
  "last_sync": "2026-01-17T10:30:00Z",
  "processed_blogs": {
    "https://clickhouse.com/blog/post-url": {
      "title": "Blog Title",
      "pub_date": "2026-01-16T13:35:16Z",
      "file_path": "blogs/2026-01-16-blog-title-slug.md",
      "processed_at": "2026-01-17T10:30:00Z"
    }
  },
  "total_blogs": 142,
  "failed_blogs": []
}
```

This ensures:
- No duplicate processing
- Resume capability after crashes
- Visibility into failed blogs

## File Naming Convention

Blog files are named: `YYYY-MM-DD-slug.md`

Where:
- `YYYY-MM-DD`: Publication date
- `slug`: URL-safe version of title (lowercase, hyphenated, max 50 chars)

Examples:
- `2026-01-15-getting-started-with-clickhouse.md`
- `2026-01-10-optimizing-query-performance.md`

## Error Handling

The system is designed to be resilient:

- **Network errors**: Automatic retry with exponential backoff (3 attempts)
- **HTTP errors**: 404/403 are logged and skipped, other errors trigger retries
- **Per-blog isolation**: One blog failure doesn't stop the entire sync
- **State preservation**: State saved after each successful blog
- **Failed blog tracking**: All failures logged in `sync_state.json`

## Combined File Format

The `all_blogs.md` file contains:
- Header with total count and last update time
- All blogs sorted by publication date (newest first)
- Each blog includes:
  - Title
  - Publication date
  - Original URL
  - Full markdown content
  - Separator between blogs

## Dependencies

- `feedparser>=6.0.11` - RSS feed parsing
- `requests>=2.31.0` - HTTP downloads
- `python-dateutil>=2.8.2` - Date parsing
- `pyyaml>=6.0.1` - YAML frontmatter (optional)

## Development

### Running Tests

Currently, the project doesn't include automated tests. To verify functionality:

1. Run a manual sync:
```bash
uv run python scripts/sync_blogs.py
```

2. Verify outputs:
   - `blogs/` directory contains MD files
   - `all_blogs.md` exists and is properly formatted
   - `sync_state.json` contains processed URLs

3. Run sync again to verify no duplicates are created

### Adding Features

The modular design makes it easy to extend:

- **StateManager**: Modify state tracking logic
- **RSSFetcher**: Change RSS source or parsing
- **MarkdownDownloader**: Customize content retrieval
- **FileManager**: Adjust file naming or combined file format
- **SlugGenerator**: Modify slug generation rules

## GitHub Actions Configuration

The workflow requires:
- **Permissions**: `contents: write` (for commits)
- **Secrets**: None required (uses `GITHUB_TOKEN` automatically)

To manually trigger the workflow:
1. Go to Actions tab in GitHub
2. Select "Sync ClickHouse Blogs"
3. Click "Run workflow"

## Troubleshooting

### No blogs downloaded

- Check RSS feed is accessible: `curl https://clickhouse.com/rss.xml`
- Check markdown endpoint works: `curl https://clickhouse.com/blog/[slug].md`
- Review `sync_state.json` for failed blogs

### Workflow not running

- Verify workflow file syntax
- Check repository permissions
- Review Actions tab for error messages

### State file corrupted

If `sync_state.json` becomes corrupted:
1. Delete the file
2. Run sync script again (will start fresh)
3. All blogs will be redownloaded

## License

This project is provided as-is for syncing ClickHouse blog content.

## Links

- [ClickHouse Official Website](https://clickhouse.com)
- [ClickHouse Blog](https://clickhouse.com/blog)
- [ClickHouse RSS Feed](https://clickhouse.com/rss.xml)
