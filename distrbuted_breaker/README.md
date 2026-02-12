# Distributed Circuit Breaker – Local PoC

## 1️⃣ Overview

This project simulates a **distributed system** with multiple service instances, each running its own independent circuit breaker.

The goal is to observe:

* How breaker state diverges across instances
* How distributed systems behave under partial failure
* Why shared breaker state might be needed
* The tradeoffs between local autonomy and global coordination

---

## 2️⃣ Architecture

### Phase 1: Independent Circuit Breakers

Each service instance maintains its own breaker state.

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
| Breaker A   |       | Breaker B   |       | Breaker C   |
+-------------+       +-------------+       +-------------+
        \                   |                    /
         \                  |                   /
          \-----------------v------------------/
                Load Generator (Client)
```

---

## 3️⃣ Project Structure

```
distributed_breaker/
│
├── common/
│   └── circuit_breaker.py
│
├── unreliable_service/
│   └── app.py
│
├── service_instance_A/
│   ├── app.py
│   └── instance_config.py
│
├── service_instance_B/
│   ├── app.py
│   └── instance_config.py
│
├── service_instance_C/
│   ├── app.py
│   └── instance_config.py
│
├── load_generator/
│   └── client.py
│
└── requirements.txt
```

---

## 4️⃣ What This System Demonstrates

### Independent Breaker Behavior

* Each instance sees failures independently.
* Breaker state diverges across instances.
* Some nodes may OPEN while others remain CLOSED.

### Real Distributed Characteristics

* Failure is not synchronized.
* Recovery timing differs.
* Partial degradation is normal.

---

## 5️⃣ Circuit Breaker Behavior

### States

* CLOSED → Normal operation
* OPEN → Requests blocked
* HALF_OPEN → Probe request allowed

### Transitions

```
CLOSED → (failures exceed threshold) → OPEN
OPEN → (timeout reached) → HALF_OPEN
HALF_OPEN → (success) → CLOSED
HALF_OPEN → (failure) → OPEN
```

---

## 6️⃣ Installation

### Requirements

* Python 3.10+
* pip

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 7️⃣ Running the System

Open **5 terminals**.

---

### Terminal 1 – Start Unreliable Service

```bash
cd unreliable_service
python app.py
```

Runs on:

```
http://localhost:9000
```

---

### Terminal 2 – Start Instance A

```bash
cd service_instance_A
python app.py
```

Port:

```
8001
```

---

### Terminal 3 – Start Instance B

```bash
cd service_instance_B
python app.py
```

Port:

```
8002
```

---

### Terminal 4 – Start Instance C

```bash
cd service_instance_C
python app.py
```

Port:

```
8003
```

---

### Terminal 5 – Start Load Generator

```bash
cd load_generator
python client.py
```

This randomly calls instances 8001, 8002, 8003.

---

## 8️⃣ What to Observe

### 1. Divergent Breaker States

Example output:

```
Instance-A → OPEN
Instance-B → CLOSED
Instance-C → HALF_OPEN
```

Each node behaves independently.

---

### 2. Fast Fail Behavior

When breaker is OPEN:

* Instance returns 503 immediately.
* No downstream call is made.
* Instance protects itself.

---

### 3. Flapping

You may see:

```
OPEN → HALF_OPEN → OPEN
```

This happens when recovery probe fails.

---

### 4. Partial System Degradation

Some instances may be OPEN while others are still sending traffic.

This mirrors real microservice behavior.

---
