from flask import Flask, jsonify
import os
import random

from static.string_randomizer import generate_string_query
from static.id_randomizer import generate_valid_video_id
from static.word_randomizer import generate_word_query

app = Flask(__name__)

@app.route('/')
def index():
    return 'YouTube Randomizer is alive. Try /api/random-video to get a random query or video ID.'

@app.route('/api/random-video')
def random_video():
    method = random.choice(['string', 'id', 'word'])

    if method == 'string':
        result = generate_string_query()
    elif method == 'id':
        result = generate_valid_video_id()
        if result is None:
            return jsonify({'error': 'No valid video ID found after retries'}), 404
    else:
        result = generate_word_query()

    return jsonify({'method': method, 'result': result})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
