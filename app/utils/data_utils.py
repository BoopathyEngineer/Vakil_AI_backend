import requests
from youtube_search import YoutubeSearch
from googlesearch import search
import requests
import re
from app.logger.logger import logger_setup

logger = logger_setup(__name__)

def get_title_fast(url, timeout=3):
    try:
        logger.info(f"Request received to fetch title for URL: {url} [status_code=100]")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=timeout, stream=True)
        content = response.iter_content(chunk_size=1024)
        html = b""
        for chunk in content:
            html += chunk
            if b"</title>" in html:
                break
        html = html.decode(errors='ignore')
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if match:
            logger.info(f"Successfully fetched title for URL: {url} [status_code=200]")
            return match.group(1).strip()
        else:
            logger.warning(f"No title found for URL: {url} [status_code=204]")
            return "No Title Found"
    except Exception as e:
        logger.error(f"Failed to fetch title for URL: {url} [status_code=500] - {e}", exc_info=True)
        return "Failed to fetch title"
    
def fetch_links(query, num_results=5):
    logger.info(f"Request received to fetch links for query: '{query}' [status_code=100]")
    results = []
    for url in search(query, num_results=20):  # fetch more, filter later
        if "youtube.com" in url or "youtu.be" in url:
            continue  # skip YouTube links
        title = get_title_fast(url)
        if title != "Failed to fetch title" and title != "No Title Found" and url:
            results.append({
                "Title": title,
                "URL": url
            })
        if len(results) >= num_results:
            break
    if results:
        logger.info(f"Successfully fetched {len(results)} links for query: '{query}' [status_code=200]")
    else:
        logger.warning(f"No valid links found for query: '{query}' [status_code=204]")
    return results

def fetch_videos(query, limit=5):
    logger.info(f"Request received to fetch videos for query: '{query}' [status_code=100]")
    results = YoutubeSearch(query, max_results=limit).to_dict()
 
    video_info = []
    for video in results:
        video_info.append({
            "Title": video['title'],
            "URL": f"https://www.youtube.com{video['url_suffix']}"
        })
    if video_info:
        logger.info(f"Successfully fetched {len(video_info)} videos for query: '{query}' [status_code=200]")
    else:
        logger.warning(f"No videos found for query: '{query}' [status_code=204]")
    return video_info
