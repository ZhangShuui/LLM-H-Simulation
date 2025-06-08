# LLM-H-Simulation

This repository demonstrates a set of API-based scrapers for major social
media platforms. The `scrapers.py` module contains functions that collect
public posts using official APIs for X (Twitter), Telegram, YouTube,
TikTok, Xiaohongshu, and Bilibili. Each function returns data grouped by
`user_id` and documents the expected post structure in comments.

These scrapers require valid API credentials and network access which are
not provided here. They are intended as examples of compliant data
collection respecting each platform's terms of service and privacy
policies.

## Command-line usage

The module can be executed directly to invoke the scrapers via command
line arguments. The basic syntax is:

```bash
python3 scrapers.py <platform> [options]
```

Each platform exposes specific parameters. For example to collect tweets:

```bash
python3 scrapers.py x --query "example" --max-results 10
```

Example shell scripts are available in the `scripts/` directory for quick
testing.

