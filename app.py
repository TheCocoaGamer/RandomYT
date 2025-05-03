from flask import Flask, jsonify, render_template
import os
import random
import requests
import re
import json
from googleapiclient.discovery import build

from static.id_randomizer import generate_valid_video_id
from static.word_randomizer import generate_word_query

app = Flask(__name__)

def scrape_youtube(query):
    """Scrape YouTube search results to get video IDs."""
    search_url = f"https://www.youtube.com/results?search_query={query}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(search_url, headers=headers)
    html = response.text

    match = re.search(r"var ytInitialData = ({.*?});", html)
    if not match:
        print("❌ Scraper: No ytInitialData found.")
        return []

    try:
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/random-video')
def random_video():
    method = random.choice(['id', 'word'])
    if method == 'id':
        query = generate_valid_video_id()
    else:
        query = generate_word_query()

    print(f"🔎 Method: {method} | Query: {query}")

    api_key = os.getenv('YT_API_KEY')
    youtube = build('youtube', 'v3', developerKey=api_key)

    filters = ["relevance", "date", "viewCount", "rating"]
    order = random.choice(filters)
    print(f"📊 Using filter: {order}")

    try:
        search_response = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=5,
            order=order,
            safeSearch='none'  # No filter
        ).execute()

        items = search_response.get('items', [])
        print(f"🔎 YouTube API returned {len(items)} result(s)")

        if not items:
            print("❗ API found no results. Trying scrape fallback...")
            video_ids = scrape_youtube(query)
            print(f"🔎 Scraper found {len(video_ids)} result(s)")
            if not video_ids:
                return jsonify({
                    'error': 'No videos found by API or scraper.',
                    'query': query,
                    'method': method,
                    'filter': order
                })
            video_id = random.choice(video_ids)
            print(f"✅ Scraper selected video ID: {video_id} | Method: {method}")
            return jsonify({
                'method': method,
                'query': query,
                'filter': order,
                'videoId': video_id,
                'fallback': 'scraper'
            })

        choice = random.choice(items)
        video_id = choice['id']['videoId']

        print(f"✅ API selected video ID: {video_id} | Method: {method}")
        return jsonify({
            'method': method,
            'query': query,
            'filter': order,
            'videoId': video_id,
            'fallback': 'api'
        })

    except Exception as e:
        print(f"🔥 ERROR fetching video: {e}")
        return jsonify({
            'error': 'Failed to fetch video.',
            'query': query,
            'method': method,
            'filter': order
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
