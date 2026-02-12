"""
This Flask application represents a service instance (Instance-A) that uses a Redis-based circuit breaker to manage calls to an unreliable service. 
It exposes an endpoint (/call) that simulates calling the unreliable service and demonstrates the behavior of the circuit breaker by allowing or blocking requests based on the current state of the circuit.
"""
from flask import Flask, jsonify
import requests
import sys
import os

sys.path.append(os.path.abspath("../common"))
from circuit_breaker import RedisCircuitBreaker

from instance_config import INSTANCE_NAME, PORT

app = Flask(__name__)
cb = RedisCircuitBreaker(service_name="unreliable_service", failure_threshold=3, recovery_timeout=10)

# Endpoint to call the unreliable service and demonstrate circuit breaker behavior
@app.route("/call")
def call_service():
    if not cb.allow_request():
        return jsonify({
            "instance": INSTANCE_NAME,
            "status": "blocked",
            "state": cb.get_state().value
        }), 503

    try:
        # Make a request to the unreliable service with a timeout to simulate potential failures
        response = requests.get("http://localhost:9000/data", timeout=1)

        if response.status_code == 200:
            cb.record_success()
            return jsonify({
                "instance": INSTANCE_NAME,
                "status": "success",
                "state": cb.get_state().value
            })

        else:
            cb.record_failure()
            return jsonify({
                "instance": INSTANCE_NAME,
                "status": "failure",
                "state": cb.get_state().value
            }), 500

    except Exception:
        cb.record_failure()
        return jsonify({
            "instance": INSTANCE_NAME,
            "status": "exception",
            "state": cb.get_state().value
        }), 500


if __name__ == "__main__":
    app.run(port=PORT)
