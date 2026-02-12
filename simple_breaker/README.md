# Simple Circuit Breaker – Proof of Concept (PoC)

## 1. Overview

This project demonstrates a simple **Circuit Breaker pattern** implementation from scratch in Python.

The goal is to:

* Prevent cascading failures
* Fail fast when a dependency is unhealthy
* Allow controlled recovery
* Understand state transitions deeply

---

## 2. Problem It Solves

When a service repeatedly calls a failing dependency:

* Threads get blocked
* Latency spikes
* Resources get exhausted
* The whole system can collapse

Circuit breaker acts as a **safety fuse**.

---

## 3. High-Level Architecture

```
+-------------+        +-------------------+        +------------------+
|   Client    | -----> |  Circuit Breaker  | -----> | Unreliable       |
|  (Caller)   |        |  (Protection)     |        | Service          |
+-------------+        +-------------------+        +------------------+
```

### Flow:

1. Client makes request
2. Circuit breaker decides:
   * Allow
   * Block
3. If allowed → call downstream service
4. Based on result → update breaker state

---

## 4. Circuit Breaker States

```
                Failure threshold reached
        CLOSED -----------------------------> OPEN
          ^                                     |
          |                                     |
          |                                     |
          | Success in HALF_OPEN                |
          |                                     |
          +--------- HALF_OPEN <----------------+
                    (after timeout)
```

---

## 5. State Definitions

### CLOSED

* Normal operation
* Requests flow through
* Failures are counted
* If failures ≥ threshold → OPEN

### OPEN

* Requests are blocked immediately
* No downstream calls made
* After timeout → HALF_OPEN

### HALF_OPEN

* Allows 1 test request
* If success → CLOSED
* If failure → OPEN again

---

## 6. State Transition Table

| Current State | Event                     | Next State |
| ------------- | ------------------------- | ---------- |
| CLOSED        | Failure count < threshold | CLOSED     |
| CLOSED        | Failure count ≥ threshold | OPEN       |
| OPEN          | Timeout not reached       | OPEN       |
| OPEN          | Timeout reached           | HALF_OPEN  |
| HALF_OPEN     | Success                   | CLOSED     |
| HALF_OPEN     | Failure                   | OPEN       |

---

## 7. Internal State Variables

| Variable            | Purpose                     |
| ------------------- | --------------------------- |
| `failure_threshold` | Max failures before opening |
| `failure_count`     | Current failure counter     |
| `recovery_timeout`  | Cooldown duration           |
| `last_failure_time` | When breaker opened         |
| `state`             | Current state               |

---

## 8. Why This Matters in Real Systems

Without circuit breaker:

```
High failure rate
    ↓
Retry storms
    ↓
Thread pool exhaustion
    ↓
Latency spike
    ↓
Total system collapse
```

With circuit breaker:

```
High failure rate
    ↓
Breaker opens
    ↓
Fast failure
    ↓
System survives
```

---

## 9. Real-World Placement

Circuit breakers typically exist:

* Inside service SDKs
* In API Gateways
* In service meshes
* In resilience middleware

For example:

```
User → API Gateway → Service A → Circuit Breaker → Service B
```

If Service B dies, Service A survives.

---

## 10. How to Run

```bash
python simple-breaker.py
```

You will observe:

* Failure accumulation
* State transitions
* Blocked requests
* Recovery attempts

---

## 11. What This PoC Does NOT Include

* Thread safety
* Sliding window failure rate
* Percentage-based failure thresholds
* Metrics integration
* Async support
* Real HTTP calls

These are next-level improvements.

---