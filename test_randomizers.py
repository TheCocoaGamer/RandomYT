import random

from static.string_randomizer import generate_string_query
from static.id_randomizer import generate_valid_video_id
from static.word_randomizer import generate_word_query

def test_randomizer():
    method = random.choice(['string', 'id', 'word'])

    if method == 'string':
        result = generate_string_query()
    elif method == 'id':
        result = generate_valid_video_id()
    else:
        result = generate_word_query()

    print(f"Method: {method}")
    print(f"Result: {result}")

if __name__ == "__main__":
    print("Testing all randomizers...\n")
    for _ in range(50):  # Run 10 test cases
        test_randomizer()
        print("-" * 40)
