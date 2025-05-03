from flask import Flask, jsonify, render_template
import os
import random
from googleapiclient.discovery import build

from static.string_randomizer import generate_string_query
from static.id_randomizer import generate_valid_video_id
from static.word_randomizer import generate_word_query

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/random-video')
def random_video():
    method = random.choice(['string', 'id', 'word'])

    if method == 'string':
        query = generate_string_query()
    elif method == 'id':
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
            order=order
        ).execute()

        items = search_response.get('items', [])
        if not items:
            print(f"❌ No videos found for query: '{query}' | Method: {method} | Filter: {order}")
            return jsonify({
                'error': 'No videos found.',
                'query': query,
                'method': method,
                'filter': order
            })

        choice = random.choice(items)
        video_id = choice['id']['videoId']

        print(f"✅ Selected video ID: {video_id} | Method: {method} | Filter: {order}")
        return jsonify({
            'method': method,
            'query': query,
            'filter': order,
            'videoId': video_id
        })

    except Exception as e:
        print(f"🔥 ERROR fetching video for query: '{query}' | Method: {method} | Filter: {order} | Error: {e}")
        return jsonify({
            'error': 'Failed to fetch video.',
            'query': query,
            'method': method,
            'filter': order
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
