import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from icrawler.builtin import GoogleImageCrawler
from icrawler.downloader import Downloader
import threading
from concurrent.futures import ThreadPoolExecutor
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

executor = ThreadPoolExecutor()

class ImageURL(Downloader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collected_images = []
        self.lock = threading.Lock()

    def download(self, task, default_ext, timeout=5, **kwargs):
        url = task.get('file_url')
        if url:
            with self.lock:
                self.collected_images.append({'source': url})

def image_crawler(query: str):
    # Store a reference to the downloader instance
    logger.info(f"Request received to crawl images for query: '{query}' [status_code=100]")
    try:
        image_downloader_instance = {}

        class CustomImageURL(ImageURL):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                image_downloader_instance['downloader'] = self

        google_crawler = GoogleImageCrawler(downloader_cls=CustomImageURL)
        google_crawler.crawl(keyword=query, max_num=5)

        return image_downloader_instance['downloader'].collected_images[:10]
    except Exception as e:
        logger.error(f"Error crawling images for query: '{query}' [status_code=500] - {e}", exc_info=True)
        return []

async def  fetch_images(query: str):
    logger.info(f"Request received to fetch images for query: '{query}' [status_code=100]")
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, image_crawler, query)