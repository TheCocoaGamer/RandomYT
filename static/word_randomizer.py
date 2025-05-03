import requests
import random

def generate_word_query():
    try:
        response = requests.get('https://api.urbandictionary.com/v0/random')
        if response.status_code == 200:
            data = response.json()
            words = [entry['word'] for entry in data.get('list', [])]
            if words:
                query = random.choice(words)
                while random.random() < 0.25:
                    query += ' ' + random.choice(words)
                return query
    except:
        pass

    return "random video"
