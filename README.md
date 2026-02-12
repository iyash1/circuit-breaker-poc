# Circuit Breaker POC 
## Overview

This repository is a progressive learning lab for understanding the **Circuit Breaker pattern**, evolving from:

1. Simple in-memory implementation
2. Multi-instance distributed simulation
3. Redis-backed shared-state distributed coordination

The goal of this project is not just to implement a pattern — but to understand:

* Failure dynamics
* Distributed inconsistency
* State coordination tradeoffs
* Resilience architecture decisions

Each folder represents a different stage in this evolution.

---

# Repository Structure

```
circuit-breaker-poc/
│
├── simple_breaker/
├── distrbuted_breaker/
├── redis_breaker/
└── .gitignore
```

---

# Directory Overview

---

## 1️⃣ `simple_breaker/`
### Purpose
Single-process, in-memory circuit breaker implementation.
This is the foundational version.
What It Demonstrates:
* CLOSED / OPEN / HALF_OPEN states
* Failure threshold logic
* Recovery timeout
* State transitions
* Basic protection mechanics

---

## 2️⃣ `distrbuted_breaker/`
### Purpose

Simulates a distributed system locally with multiple service instances.
Each instance:
* Maintains its own breaker state
* Observes failures independently
* Transitions independently

---

## 3️⃣ `redis_breaker/`
### Purpose

Implements a Redis-backed shared-state circuit breaker.
All instances:
* Read state from Redis
* Write failures to Redis
* Transition state globally

---

# Learning Progression
This project is designed to be explored in order:

1️⃣ `simple_breaker`
2️⃣ `distrbuted_breaker`
3️⃣ `redis_breaker`

Each stage introduces one additional systems design dimension:

| Stage       | Concept Introduced                |
| ----------- | --------------------------------- |
| Simple      | State machine logic               |
| Distributed | Divergent state & autonomy        |
| Redis       | Shared coordination & consistency |

---

# Common Prerequisites

For all projects:

* Python 3.10+
* pip

For distributed and Redis versions:

* Flask
* requests

For Redis version:

* Redis server running locally

Install dependencies inside each project directory:

```bash
pip install -r requirements.txt
```

---

# Known Limitations (Across Versions)

These implementations are intentionally simplified for learning.

Missing production features:

* Sliding window failure rate
* Slow-call detection
* Proper distributed locking for HALF_OPEN
* Metrics/observability
* Prometheus integration
* Lua-based atomic transitions
* High availability Redis
* Circuit state TTL management
* Retry strategy integration
* Bulkhead isolation

These can be added as future enhancements.

---