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

# Initialize environment and API
load_dotenv()
AGENTQL_API_KEY = os.getenv('AGENTQL_API_KEY')
if not AGENTQL_API_KEY:
    raise ValueError("AGENTQL_API_KEY not found in environment variables")
agentql.configure(api_key=AGENTQL_API_KEY)

# Global storage for video data
all_videos = []

async def human_like_scroll(page):
    """Simulates human scrolling behavior to load all playlist items"""
    current_position = 0
    scroll_batch_size = 1000
    
    logger.info("Starting scroll process...")
    scroll_start_time = datetime.now()
    
    # Get initial page height
    total_height = await page.evaluate('document.documentElement.scrollHeight')
    
    while True:
        # Scroll down by batch size
        await page.evaluate(f'window.scrollTo(0, {current_position + scroll_batch_size})')
        current_position += scroll_batch_size
        
        # Add small delay between scrolls
        await asyncio.sleep(0.2)
        
        # Check if reached bottom of page
        new_height = await page.evaluate('document.documentElement.scrollHeight')
        if new_height == total_height and current_position > total_height:
            break
        total_height = new_height
    
    scroll_duration = (datetime.now() - scroll_start_time).total_seconds()
    logger.info(f"Scrolling completed in {scroll_duration:.2f} seconds")
    
    # Extract video data after scrolling complete
    logger.info("Starting video data extraction...")
    query_start_time = datetime.now()
    await query_visible_videos(page)
    query_duration = (datetime.now() - query_start_time).total_seconds()
    logger.info(f"Data extraction completed in {query_duration:.2f} seconds")

async def query_visible_videos(page):
    """Extracts data using simple AgentQL query based on documentation"""
    PLAYLIST_QUERY = """
    {
        videos[] {
            title
            views
            age
            link
            thumbnail
        }
    }
    """
    
    try:
        response = await page.query_data(PLAYLIST_QUERY)
        if response and 'videos' in response:
            new_videos = []
            
            for video in response['videos']:
                video_id = video.get('link', '').split('v=')[1].split('&')[0] if 'v=' in video.get('link', '') else None
                
                if not video_id or any(v.get('id') == video_id for v in all_videos):
                    continue
                
                formatted_video = {
                    'title': video.get('title', ''),
                    'views': video.get('views', ''),
                    'age': video.get('age', ''),
                    'thumbnail': video.get('thumbnail', ''),
                    'link': video.get('link', ''),
                    'id': video_id,
                    'toggle': 'ON'
                }
                
                new_videos.append(formatted_video)
                logger.info(f"Found new video: {formatted_video['title']}")
            
            if new_videos:
                all_videos.extend(new_videos)
                logger.info(f"Added {len(new_videos)} new videos")
                
    except Exception as e:
        logger.error(f"Error querying video data: {str(e)}")
        await asyncio.sleep(5)  # Backoff strategy

async def save_data(output_dir="output"):
    """Asynchronous data saving"""
    if not all_videos:
        logger.warning("No videos to save")
        return

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"playlist_data_{timestamp}"
    
    async def save_json():
        json_path = os.path.join(output_dir, f"{base_filename}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(all_videos, f, ensure_ascii=False, indent=4)
    
    async def save_csv():
        csv_path = os.path.join(output_dir, f"{base_filename}.csv")
        columns = ['title', 'age', 'views', 'thumbnail', 'link', 'id', 'toggle']
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(all_videos)
    
    async def save_excel():
        excel_path = os.path.join(output_dir, f"{base_filename}.xlsx")
        wb = Workbook()
        ws = wb.active
        columns = ['title', 'age', 'views', 'thumbnail', 'link', 'id', 'toggle']
        ws.append(columns)
        
        for video in all_videos:
            ws.append([video.get(col, '') for col in columns])
        
        dv = DataValidation(type="list", formula1='"ON,OFF"', allow_blank=False)
        dv.add(f'G2:G{len(all_videos) + 1}')
        ws.add_data_validation(dv)
        wb.save(excel_path)
    
    # Run saves in parallel
    await asyncio.gather(save_json(), save_csv(), save_excel())

async def scrape_playlist():
    """Main function to orchestrate playlist scraping"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = agentql.wrap(await browser.new_page())
        
        # Only use stealth mode - remove fast mode
        await page.enable_stealth_mode(
            webgl_vendor="Intel Inc.",
            webgl_renderer="Intel Iris OpenGL Engine",
            nav_user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Load playlist page
        await page.goto('https://www.youtube.com/playlist?list=PLPJVlVRVmhc4Z01fD57jbzycm9I6W054x')
        await page.wait_for_selector('ytd-playlist-video-renderer', timeout=10000)
        await asyncio.sleep(2)

        # Scroll and collect data
        await human_like_scroll(page)
        await save_data()
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_playlist()) 