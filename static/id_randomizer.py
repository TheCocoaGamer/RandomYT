import random
import string

def generate_short_query():
    allowed_chars = string.ascii_letters + string.digits
    length = random.choice([4, 5, 6])
    return ''.join(random.choice(allowed_chars) for _ in range(length))
