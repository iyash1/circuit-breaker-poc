"""
Defines a simple circuit breaker implementation to manage the state of service calls in the other service instances.
The CircuitBreaker class tracks the number of consecutive failures and manages state transitions between CLOSED, OPEN,
and HALF_OPEN based on the configured failure threshold and recovery timeout.
"""
import time
from enum import Enum

# CircuitState defines the possible states of the circuit breaker: CLOSED, OPEN, and HALF_OPEN.
class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

# CircuitBreaker class manages the state of the circuit and handles transitions based on success and failure of service calls.
class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=5):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

    # Allow a request if the circuit is CLOSED or if it's HALF_OPEN (allowing a test request). If OPEN, check if the recovery timeout has elapsed to transition to HALF_OPEN.
    def allow_request(self):
        if self.state == CircuitState.OPEN:
            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                print("⚠️ HALF_OPEN")
                return True
            return False
        return True

    # Record a successful service call. If the circuit is HALF_OPEN, transition back to CLOSED. Otherwise, reset the failure count.
    def record_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            print("✅ CLOSED")
        else:
            self.failure_count = 0

    # Record a failed service call. If the circuit is HALF_OPEN, transition to OPEN. If the failure count exceeds the threshold, transition to OPEN.
    def record_failure(self):
        self.failure_count += 1
        print(f"❌ Failure count: {self.failure_count}")

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.last_failure_time = time.time()
            print("🚨 OPEN")
            return

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_failure_time = time.time()
            print("🚨 OPEN")
