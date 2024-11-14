
# YouTube Playlist Data Scraper

A Python-based tool that asynchronously scrapes YouTube playlist data using Playwright and AgentQL, saving the results in multiple formats (JSON, CSV, Excel) with video state toggling functionality.

## Features

- Asynchronous scraping of YouTube playlist data including:
  - Video titles
  - View counts
  - Upload dates/age
  - Thumbnails
  - Video links
- Human-like scrolling behavior to avoid detection
- Stealth mode using AgentQL
- Multi-format data export (JSON, CSV, Excel)
- Excel file with ON/OFF toggle functionality
- Comprehensive logging
- Automated testing suite

## Requirements

- Python 3.8+
- AgentQL API key (obtain from [dev.agentql.com](https://dev.agentql.com))
- Chromium browser (installed automatically)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SimonAsche/YTS06Aql.git
cd youtube-playlist-scraper
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Create a `.env` file in the project root:
```
AGENTQL_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

```python
from youtube_playlist import scrape_playlist
import asyncio

asyncio.run(scrape_playlist())
```

### Output Files

The script creates an `output` directory containing:
- `playlist_data_TIMESTAMP.json` - Raw data in JSON format
- `playlist_data_TIMESTAMP.csv` - CSV format with toggle states
- `playlist_data_TIMESTAMP.xlsx` - Excel file with dropdown toggles

### Development Installation

For development with testing tools:
```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/
```

## Project Structure

```
youtube-playlist-scraper/
├── src/
│   └── youtube_playlist/
│       ├── __init__.py
│       └── youtube_playlist.py
├── tests/
│   └── test_youtube_playlist.py
├── setup.py
├── requirements.txt
├── .env
└── README.md
```

## Dependencies

Core dependencies:
```python:setup.py
startLine: 7
endLine: 14
```

Development dependencies:
```python:setup.py
startLine: 16
endLine: 21
```

## Testing

The project includes a comprehensive test suite that verifies:
- Playlist page loading
- Data query functionality
- Scroll behavior
- API key validation

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`pip install -e ".[dev]"`)
4. Run tests to ensure everything works (`pytest tests/`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Playwright](https://playwright.dev/) for browser automation
- [AgentQL](https://dev.agentql.com/) for stealth mode and data extraction
- [OpenPyXL](https://openpyxl.readthedocs.io/) for Excel file handling
```

This README references the following code sections:

```1:14:src/youtube_playlist/youtube_playlist.py
from playwright.async_api import async_playwright
import agentql
from loguru import logger
import os
from dotenv import load_dotenv
import random
import asyncio
import json
import pandas as pd
from datetime import datetime
import csv
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
import openpyxl
```



```7:21:setup.py
    install_requires=[
        "playwright>=1.41.0",
        "agentql>=0.5.0",
        "pandas>=2.1.4",
        "python-dotenv>=1.0.0",
        "loguru>=0.7.2",
        "openpyxl>=3.1.2",
    ],
    extras_require={
        'dev': [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "pytest-asyncio>=0.23.0",
        ]
```



```40:91:tests/test_youtube_playlist.py
async def test_playlist_loading(page, api_key):
    """Test if the playlist page loads successfully"""
    logger.info("Starting test: test_playlist_loading")
    try:
        agentql.configure(api_key=api_key)
        logger.debug(f"Configured AgentQL with API key: {api_key}")
        test_url = 'https://www.youtube.com/playlist?list=PLPJVlVRVmhc4Z01fD57jbzycm9I6W054x'
        logger.debug(f"Navigating to URL: {test_url}")
        await page.goto(test_url)
        logger.debug(f"Navigated to URL: {page.url}")
        assert page.url.startswith('https://www.youtube.com/playlist')
        logger.info("test_playlist_loading passed")
    except Exception as e:
        logger.exception("Exception occurred in test_playlist_loading")
        raise

async def test_playlist_query(page, api_key):
    """Test if the playlist query returns expected data structure"""
    logger.info("Starting test: test_playlist_query")
    try:
        agentql.configure(api_key=api_key)
        logger.debug("Configured AgentQL with API key")
        
        # First navigate to the page
        test_url = 'https://www.youtube.com/playlist?list=PLPJVlVRVmhc4Z01fD57jbzycm9I6W054x'
        await page.goto(test_url)
        
        PLAYLIST_QUERY = """
        {
            videos[] {
                title
                description
                duration
                views
                uploaded_date
                url
            }
        }
        """
        logger.debug(f"Executing PLAYLIST_QUERY: {PLAYLIST_QUERY}")
        # Use query_data instead of queryElements
        response = await page.query_data(PLAYLIST_QUERY)
        logger.debug(f"Received response: {response}")
        assert response is not None
        logger.debug("Response is not None")
        assert 'videos' in response
        logger.debug("Response has 'videos' key")
        assert len(response['videos']) > 0  # Check if we got any videos
        logger.info("test_playlist_query passed")
    except Exception as e:
        logger.exception("Exception occurred in test_playlist_query")
        raise
```
# YTS06Aql
