"""
A Redis-based Circuit Breaker implementation for distributed state management across multiple service instances.
This module defines the RedisCircuitBreaker class, which uses Redis to store and manage the state of the circuit breaker,
allowing multiple service instances to share the same state and coordinate their behavior based on the
success or failure of service calls. The circuit breaker transitions between CLOSED, OPEN, and HALF_OPEN states based on 
the configured failure threshold and recovery timeout, and provides methods to allow or block requests accordingly.
"""
import time
from enum import Enum
import redis

# CircuitState defines the possible states of the circuit breaker: CLOSED, OPEN, and HALF_OPEN.
class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

# CircuitBreaker class manages the state of the circuit and handles transitions based on success and failure of service calls.
class RedisCircuitBreaker:
    # Initialize the circuit breaker with a service name, failure threshold, recovery timeout, and Redis connection parameters. 
    # The service name is used to create unique keys in Redis for tracking the state and failures of the circuit breaker.
    def __init__(
        self,
        service_name,
        failure_threshold=3,
        recovery_timeout=10,
        redis_host="localhost",
        redis_port=6379,
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        # Initialize Redis client and set up keys for state, failure count, and last failure time.
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

        self.state_key = f"cb:{service_name}:state"
        self.failure_key = f"cb:{service_name}:failures"
        self.time_key = f"cb:{service_name}:last_failure"

        # Ensure that the circuit breaker state is initialized in Redis if it doesn't already exist.
        if not self.redis.exists(self.state_key):
            self.redis.set(self.state_key, CircuitState.CLOSED.value)
            self.redis.set(self.failure_key, 0)

    # Get the current state of the circuit breaker from Redis.
    def get_state(self):
        state = self.redis.get(self.state_key)
        return CircuitState(state)

    # Determine if a request should be allowed based on the current state of the circuit. If the circuit is OPEN, check if the recovery timeout has elapsed to transition to HALF_OPEN.
    def allow_request(self):
        state = self.get_state()

        if state == CircuitState.OPEN:
            last_failure = self.redis.get(self.time_key)
            if last_failure:
                elapsed = time.time() - float(last_failure)
                if elapsed >= self.recovery_timeout:
                    self.redis.set(self.state_key, CircuitState.HALF_OPEN.value)
                    print("⚠️ HALF_OPEN")
                    return True
            return False

        return True

    # Record a successful service call. If the circuit is HALF_OPEN, transition back to CLOSED. Otherwise, reset the failure count.
    def record_success(self):
        state = self.get_state()

        if state == CircuitState.HALF_OPEN:
            self.redis.set(self.state_key, CircuitState.CLOSED.value)
            self.redis.set(self.failure_key, 0)
            print("✅ CLOSED")
        else:
            self.redis.set(self.failure_key, 0)

    # Record a failed service call. If the circuit is HALF_OPEN, transition to OPEN immediately. If the failure count exceeds the threshold, transition to OPEN.
    def record_failure(self):
        failures = int(self.redis.get(self.failure_key) or 0)
        failures += 1
        self.redis.set(self.failure_key, failures)

        print(f"❌ Shared Failure count: {failures}")

        state = self.get_state()

        if state == CircuitState.HALF_OPEN:
            self._open()
            return

        if failures >= self.failure_threshold:
            self._open()

    # Transition the circuit to OPEN state, recording the time of the last failure.
    def _open(self):
        self.redis.set(self.state_key, CircuitState.OPEN.value)
        self.redis.set(self.time_key, time.time())
        print("🚨 OPEN (Shared)")
