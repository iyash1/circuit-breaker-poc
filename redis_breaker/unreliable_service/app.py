"""
This module defines a simple Flask application that simulates an unreliable service. 
The service randomly fails to demonstrate the behavior of a circuit breaker in the other service instances.
"""
from flask import Flask
import random

app = Flask(__name__)

@app.route("/data")
def get_data():
    if random.random() < 0.6:
        return {"error": "Service failed"}, 500
    return {"message": "Success"}, 200


if __name__ == "__main__":
    app.run(port=9000)
