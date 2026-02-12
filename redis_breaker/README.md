# Distributed Circuit Breaker – Redis-Backed Version

## 1️⃣ Overview

This version upgrades the distributed circuit breaker PoC by introducing **shared state via Redis**.

Instead of each service instance maintaining its own breaker state in memory, all instances coordinate using Redis.

---

## 2️⃣ Architecture
### Redis-Backed Shared Breaker

```
                    +----------------------+
                    |  Unreliable Service  |
                    |      Port 9000       |
                    +----------^-----------+
                               |
      -----------------------------------------------------
      |                     |                     |
+-------------+       +-------------+       +-------------+
| Instance A  |       | Instance B  |       | Instance C  |
| Port 8001   |       | Port 8002   |       | Port 8003   |
|             |       |             |       |             |
|        Redis Shared Circuit Breaker State                |
|                (localhost:6379)                          |
+----------------------------------------------------------+
```

All instances:

* Read state from Redis
* Increment failure count atomically
* Transition state globally

---

## 3️⃣ Redis Keys Used

For a service name: `"unreliable_service"`

Keys:

```
cb:unreliable_service:state
cb:unreliable_service:failures
cb:unreliable_service:last_failure
```

### Example Values

| Key          | Example Value |
| ------------ | ------------- |
| state        | open          |
| failures     | 3             |
| last_failure | 1707652212.25 |

---

## 4️⃣ Running the Redis Version

### Step 1 – Start Redis

```bash
redis-server
```

Verify:

```bash
redis-cli ping
```

Expected:

```
PONG
```

---

### Step 2 – Clear Existing State

Always reset before testing:

```bash
redis-cli flushall
```

---

### Step 3 – Terminal-1 : Start Unreliable Service

```bash
cd unreliable_service
python app.py
```

Port: 9000

---

### Step 4 – Terminal-2,3,4 : Start Service Instances

Terminal-2 Instance A:

```bash
cd service_instance_A
python app.py
```

Terminal-3 Instance B:

```bash
cd service_instance_B
python app.py
```

Terminal-4 Instance C:

```bash
cd service_instance_C
python app.py
```

---

### Step 5 – Terminal-5 : Start Load Generator

```bash
cd load_generator
python client.py
```

---

## 6️⃣ What You Should Observe

### Global Circuit Opening

When failure threshold is reached:

```
🚨 OPEN (Shared)
```

All instances begin returning:

```
503 blocked
```

Even if only one instance triggered it.

---

### Coordinated HALF_OPEN

After recovery timeout:

* One instance may trigger HALF_OPEN.
* Others observe state change.

Note:
This implementation does NOT prevent multiple nodes from probing simultaneously.

---

## 7️⃣ Known Limitations (Intentional for Learning)

This implementation is NOT production-ready.

Missing features:

* Atomic state transitions (OPEN/HALF_OPEN race conditions possible)
* Proper distributed locking for HALF_OPEN
* Sliding window failure rate
* Slow-call detection
* Metrics & observability
* Lua-based atomic state logic
* Redis high-availability handling
* Circuit state TTL management

These are advanced topics.

---

## 8️⃣ Next Possible Improvements

To move toward production-grade:

* Use Redis `INCR` for atomic failure increments
* Use Lua scripts for atomic transitions
* Implement distributed lock for HALF_OPEN probe
* Add sliding window failure rate
* Add slow-call threshold
* Add metrics export (Prometheus)
* Introduce fallback strategy

---
