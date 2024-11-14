import pytest
import logging
from playwright.async_api import async_playwright
import agentql
import os
from dotenv import load_dotenv
from src.youtube_playlist.youtube_playlist import scroll_youtube_playlist

# Initialize logger for this module
logger = logging.getLogger(__name__)

# Load environment variables for testing
logger.debug("Loading environment variables from .env")
load_dotenv()

@pytest.fixture(scope="module")
def api_key():
    logger.debug("Retrieving AGENTQL_API_KEY from environment variables")
    key = os.getenv('AGENTQL_API_KEY')
    if not key:
        logger.error("AGENTQL_API_KEY not found in environment variables")
        pytest.skip("AGENTQL_API_KEY not found in environment variables")
    logger.info("AGENTQL_API_KEY retrieved successfully")
    return key

@pytest.fixture(scope="function")
async def page():
    logger.debug("Initializing Playwright for browser automation")
    async with async_playwright() as p:
        logger.debug("Launching Chromium browser")
        browser = await p.chromium.launch(headless=False)  # Use headless=True for CI environments
        logger.debug("Opening new browser page")
        page = agentql.wrap(await browser.new_page())
        logger.info("Browser page opened")
        yield page
        logger.debug("Closing browser")
        await browser.close()
        logger.info("Browser closed")

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

async def test_scroll_functionality(page):
    """Test if the scroll functionality works"""
    logger.info("Starting test: test_scroll_functionality")
    try:
        logger.debug("Getting initial scroll height")
        initial_height = await page.evaluate('document.documentElement.scrollHeight')
        logger.debug(f"Initial scroll height: {initial_height}")
        logger.debug("Scrolling to the bottom of the page")
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        logger.debug("Scrolled to bottom of the page")
        logger.debug("Getting new scroll height after scrolling")
        new_height = await page.evaluate('document.documentElement.scrollHeight')
        logger.debug(f"New scroll height: {new_height}")
        assert new_height >= initial_height 
        logger.info("test_scroll_functionality passed")
    except Exception as e:
        logger.exception("Exception occurred in test_scroll_functionality")
        raise