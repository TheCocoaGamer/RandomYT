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

    # Perform YouTube search from the BACKEND
    api_key = os.getenv('YT_API_KEY')
    youtube = build('youtube', 'v3', developerKey=api_key)

    filters = ["relevance", "date", "viewCount", "rating"]
    order = random.choice(filters)

    search_response = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=5,
        order=order
    ).execute()

    items = search_response.get('items', [])
    if not items:
        return jsonify({'error': 'No videos found.'})

    choice = random.choice(items)
    video_id = choice['id']['videoId']

    return jsonify({
        'method': method,
        'query': query,
        'videoId': video_id
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
