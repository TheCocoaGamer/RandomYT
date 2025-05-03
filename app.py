from flask import Flask
import os

app = Flask(__name__)

YT_API_KEY = os.getenv('YT_API_KEY')

@app.route('/')
def index():
    return 'YouTube Randomizer is alive. Logic coming soon.'

if __name__ == '__main__':
    app.run()
