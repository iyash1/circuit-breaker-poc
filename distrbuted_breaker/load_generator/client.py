"""
Docstring for distrbuted_breaker.load_generator.client
It randomly selects a target instance(A/B/C) and prints the response or any errors encountered.
"""
import requests
import random
import time

instances = [
    "http://localhost:8001/call",
    "http://localhost:8002/call",
    "http://localhost:8003/call",
]

while True:
    target = random.choice(instances)
    try:
        response = requests.get(target)
        print(response.json())
    except Exception as e:
        print("Error:", e)

    time.sleep(1)
