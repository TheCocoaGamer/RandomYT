from flask import Flask, jsonify, render_template
import os
import random
import requests
import re
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from static.id_randomizer import generate_valid_video_id
from static.word_randomizer import generate_word_query

app = Flask(__name__)

# ---------- Scraper function ----------
def scrape_youtube(query):
    """Scrape YouTube search results to get video IDs."""
    search_url = f"https://www.youtube.com/results?search_query={query}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(search_url, headers=headers)
        html = response.text

        match = re.search(r"var ytInitialData = ({.*?});", html)
        if not match:
            print("❌ Scraper: No ytInitialData found.")
            return []

        data_json = match.group(1)
        data = json.loads(data_json)

        video_ids = []
        contents = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"]
        for section in contents:
            item_section = section.get("itemSectionRenderer", {}).get("contents", [])
            for item in item_section:
                video_renderer = item.get("videoRenderer")
                if video_renderer and "videoId" in video_renderer:
                    video_ids.append(video_renderer["videoId"])

        return video_ids

    except Exception as e:
        print(f"🔥 Scraper parsing failed: {e}")
        return []

# ---------- Query generator ----------
def generate_query():
    method = random.choice(['id', 'word'])

    if method == 'id':
        query = generate_valid_video_id()
    else:
        query = generate_word_query()

    return method, query

# ---------- API Search ----------
def search_youtube_api(query):
    api_key = os.getenv('YT_API_KEY')

    if not api_key:
        print("❌ No YouTube API key available. Skipping API search.")
        return None, None

    youtube = build('youtube', 'v3', developerKey=api_key)

    filters = ["relevance", "date", "viewCount", "rating"]
    order = random.choice(filters)

    print(f"🔎 Trying API search: '{query}' | Filter: {order}")

    try:
        search_response = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=50,
            order=order,
            safeSearch='none'
        ).execute()

        items = search_response.get('items', [])
        print(f"🔎 YouTube API returned {len(items)} result(s)")

        if not items:
            return None, order

        choice = random.choice(items)
        video_id = choice['id']['videoId']

        print(f"✅ API selected video ID: {video_id}")
        return video_id, order

    except HttpError as e:
        print(f"🔥 API search error (quota?): {e}")
        return None, None

    except Exception as e:
        print(f"🔥 Unexpected API error: {e}")
        return None, None

# ---------- Video search logic ----------
def search_video(query):
    video_id, order = search_youtube_api(query)

    if video_id:
        return video_id, order, 'api'

    print("🔄 API failed or returned no results. Trying scraper fallback...")
    video_ids = scrape_youtube(query)

    if video_ids:
        video_id = random.choice(video_ids[:50])  # Top 50 results only
        print(f"✅ Scraper selected video ID: {video_id}")
        return video_id, order or 'n/a', 'scraper'
    else:
        print("❌ Scraper also failed to find a video.")
        return None, order or 'n/a', 'scraper'

# ---------- Routes ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/random-video')
def random_video():
    method, query = generate_query()

    print(f"🧠 Method: {method} | Query: {query}")

    video_id, filter_used, source = search_video(query)

    if video_id:
        return jsonify({
            'method': method,
            'query': query,
            'filter': filter_used,
            'videoId': video_id,
            'fallback': source
        })
    else:
        return jsonify({
            'method': method,
            'query': query,
            'filter': filter_used,
            'videoId': None,
            'fallback': source
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
