# A simple implementation of the Circuit Breaker pattern in Python.
import time, random
from enum import Enum

# CircuitState defines the possible states of the circuit breaker: CLOSED, OPEN, and HALF_OPEN.
class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

# CircuitBreaker class manages the state of the circuit and handles transitions based on success and failure of service calls.
class CircuitBreaker:
    # Initialize the circuit breaker with a failure threshold and recovery timeout.
    def __init__(
        self,
        failure_threshold=3,
        recovery_timeout=5,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        # Start in the CLOSED state, with no failures recorded.
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    # Transition the circuit to OPEN state, recording the time of the last failure.
    def _transition_to_open(self):
        self.state = CircuitState.OPEN
        self.last_failure_time = time.time()
        print("🚨 Circuit transitioned to OPEN")

    # Transition the circuit to HALF_OPEN state, allowing a test request to check if the service has recovered.
    def _transition_to_half_open(self):
        self.state = CircuitState.HALF_OPEN
        print("⚠️ Circuit transitioned to HALF_OPEN")

    # Transition the circuit back to CLOSED state, resetting failure count and last failure time.
    def _transition_to_closed(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        print("✅ Circuit transitioned to CLOSED")

    # Determine if a request should be allowed based on the current state of the circuit.
    def allow_request(self):
        if self.state == CircuitState.OPEN: # If the circuit is OPEN, check if the recovery timeout has elapsed to transition to HALF_OPEN.
            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.recovery_timeout:
                self._transition_to_half_open()
                return True
            return False

        return True

    # Record a successful service call. If the circuit is HALF_OPEN, transition back to CLOSED. Otherwise, reset the failure count.
    def record_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self._transition_to_closed()
        else:
            self.failure_count = 0

    # Record a failed service call. If the circuit is HALF_OPEN, transition to OPEN immediately. If the failure count exceeds the threshold, transition to OPEN.
    def record_failure(self):
        self.failure_count += 1
        print(f"❌ Failure count = {self.failure_count}")

        if self.state == CircuitState.HALF_OPEN:
            self._transition_to_open()
            return

        if self.failure_count >= self.failure_threshold:
            self._transition_to_open()

# Simulate an unreliable service that fails 60% of the time.
def unreliable_service():
    # Randomly fail 60% 
    if random.random() < 0.6:
        raise Exception("Service failed")
    return "Service success"

# Call the service through the circuit breaker, handling the logic for allowing requests and recording successes or failures.
def call_service(cb: CircuitBreaker):
    # Check if the circuit breaker allows the request. If not, print a message and return.
    if not cb.allow_request():
        print("⛔ Request blocked (circuit OPEN)")
        return

    # Attempt to call the unreliable service. If it succeeds, print the result and record a success. If it fails, catch the exception, print the error, and record a failure.
    try:
        result = unreliable_service()
        print(f"✅ {result}")
        cb.record_success()
    except Exception as e:
        print(f"🔥 {e}")
        cb.record_failure()


if __name__ == "__main__":
    # Create a CircuitBreaker instance with a failure threshold of 3 and a recovery timeout of 5 seconds. 
    cb = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=5,
    )

    # Then, simulate 20 attempts to call the service, printing the state of the circuit breaker before each attempt and sleeping for 1 second between attempts.
    for i in range(20):
        print(f"\n--- Attempt {i + 1} --- State: {cb.state.value}")
        call_service(cb)
        time.sleep(1) # Sleep for a bit before the next attempt to simulate time passing and allow for recovery if the circuit is OPEN.
