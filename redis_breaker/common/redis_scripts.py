"""
Redis Lua scripts for atomic operations in the circuit breaker.
"""

"""
For OPEN_SCRIPT:
KEYS[1] → state_key
KEYS[2] → time_key
KEYS[3] → probe_lock_key
ARGV[1] → "open"
ARGV[2] → timestamp
"""

OPEN_SCRIPT = """
redis.call("SET", KEYS[1], ARGV[1])
redis.call("SET", KEYS[2], ARGV[2])
redis.call("DEL", KEYS[3])
return 1
"""

"""
For FAILURE_SCRIPT:
KEYS[1] → failure_key
KEYS[2] → state_key
KEYS[3] → time_key
KEYS[4] → probe_lock_key
ARGV[1] → failure_threshold
ARGV[2] → "open"
ARGV[3] → timestamp
"""

FAILURE_SCRIPT = """
local failures = redis.call("INCR", KEYS[1])
if failures >= tonumber(ARGV[1]) then
    redis.call("SET", KEYS[2], ARGV[2])
    redis.call("SET", KEYS[3], ARGV[3])
    redis.call("DEL", KEYS[4])
end
return failures
"""

"""
For HALF_OPEN_SCRIPT:
KEYS[1] → state_key
ARGV[1] → lock_value
ARGV[2] → "half_open" (new state)
"""

HALF_OPEN_SCRIPT = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    redis.call("SET", KEYS[1], ARGV[2])
    return 1
end
return 0
"""
