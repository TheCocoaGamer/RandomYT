import random
import string

def generate_string_query():
    letters = list(string.ascii_uppercase)
    result = [letter for letter in letters if random.randint(1, 100) <= random.randint(10, 90)]
    if random.random() < 0.85:
        random.shuffle(result)
    query = ''.join(result)
    if random.random() < 0.25:
        query += ' ' + ''.join(random.sample(letters, random.randint(2, 6)))
    return query
