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
from redis_scripts import OPEN_SCRIPT, FAILURE_SCRIPT, HALF_OPEN_SCRIPT

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
        self.open_script = self.redis.register_script(OPEN_SCRIPT)
        self.failure_script = self.redis.register_script(FAILURE_SCRIPT)
        self.half_open_script = self.redis.register_script(HALF_OPEN_SCRIPT)


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
    # In the OPEN state, only one request is allowed to pass through as a probe to test if the service has recovered. If the probe request is successful, the circuit transitions back to CLOSED. If it fails, the circuit remains OPEN.
    def allow_request(self):
        state = self.get_state()

        if state == CircuitState.OPEN:
            last_failure = self.redis.get(self.time_key)
            if not last_failure:
                return False

            elapsed = time.time() - float(last_failure)

            if elapsed < self.recovery_timeout:
                return False

            # STEP 1: Try to acquire probe lock
            lock_acquired = self.redis.set(
                f"{self.service_name}:probe_lock",
                "1",
                nx=True,
                ex=5
            )

            if not lock_acquired:
                return False  # Someone else is probing

            # STEP 2: Transition to HALF_OPEN safely
            transitioned = self.half_open_script(
                keys=[self.state_key],
                args=[CircuitState.OPEN.value, CircuitState.HALF_OPEN.value],
            )

            if transitioned:
                print("⚠️ HALF_OPEN (Probe Leader)")
                return True
            else:
                return False

        if state == CircuitState.HALF_OPEN:
            return False

        return True


    # Record a successful service call. If the circuit is HALF_OPEN, transition back to CLOSED. Otherwise, reset the failure count.
    def record_success(self):
        state = self.get_state()

        if state == CircuitState.HALF_OPEN:
            self.redis.set(self.state_key, CircuitState.CLOSED.value)
            self.redis.set(self.failure_key, 0)
            self.redis.delete(f"{self.service_name}:probe_lock")
            print("✅ CLOSED (Shared)")
        else:
            self.redis.set(self.failure_key, 0)


    # Record a failed service call. If the circuit is HALF_OPEN, transition to OPEN immediately. If the failure count exceeds the threshold, transition to OPEN.
    def record_failure(self):
        failures = self.failure_script(
            keys=[
                self.failure_key,
                self.state_key,
                self.time_key,
                f"{self.service_name}:probe_lock",
            ],
            args=[
                self.failure_threshold,
                CircuitState.OPEN.value,
                time.time(),
            ],
        )

        print(f"❌ Shared Failure count: {failures}")


    # Transition the circuit to OPEN state, recording the time of the last failure.
    def _open(self):
        self.open_script(
            keys=[self.state_key, self.time_key, f"{self.service_name}:probe_lock"],
            args=[CircuitState.OPEN.value, time.time()],
        )
        print("🚨 OPEN (Atomic Shared)")


