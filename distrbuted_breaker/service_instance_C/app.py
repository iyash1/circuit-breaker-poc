from flask import Flask, jsonify
import requests
import sys
import os

sys.path.append(os.path.abspath("../common"))
from circuit_breaker import CircuitBreaker

from instance_config import INSTANCE_NAME, PORT

app = Flask(__name__)
cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10)


@app.route("/call")
def call_service():
    if not cb.allow_request():
        return jsonify({
            "instance": INSTANCE_NAME,
            "status": "blocked",
            "state": cb.state.value
        }), 503

    try:
        response = requests.get("http://localhost:9000/data", timeout=1)

        if response.status_code == 200:
            cb.record_success()
            return jsonify({
                "instance": INSTANCE_NAME,
                "status": "success",
                "state": cb.state.value
            })

        else:
            cb.record_failure()
            return jsonify({
                "instance": INSTANCE_NAME,
                "status": "failure",
                "state": cb.state.value
            }), 500

    except Exception:
        cb.record_failure()
        return jsonify({
            "instance": INSTANCE_NAME,
            "status": "exception",
            "state": cb.state.value
        }), 500


if __name__ == "__main__":
    app.run(port=PORT)
