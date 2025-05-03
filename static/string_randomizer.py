import random
import string

def generate_string_query():
    letters = list(string.ascii_uppercase)
    kept_letters = []

    for letter in letters:
        if random.randint(10, 90) >= random.randint(1, 100):
            kept_letters.append(letter)

    if random.random() < 0.85:
        random.shuffle(kept_letters)

    query = ''.join(kept_letters)

    if random.random() < 0.25:
        query += ' ' + generate_string_query()

    return query
