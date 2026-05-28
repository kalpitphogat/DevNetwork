"""
Upstash Redis Checkpoint Store — for state checkpointing and crash recovery.

Caches intermediate agent run states. If a crash or timeout occurs,
resumes from the last successful checkpoint instead of starting from scratch.
Gracefully falls back to local memory if REDIS_URL is not set.
"""
import os
import json
import redis

_in_memory_checkpoints = {}


def _redis_url() -> str:
    """Read REDIS_URL at call time so late-loaded .env values are picked up."""
    return os.getenv("REDIS_URL", "")


def get_redis_client():
    """Get a Redis client instance if REDIS_URL is configured."""
    url = _redis_url()
    if not url:
        return None
    try:
        # upstash connection via standard redis client
        client = redis.Redis.from_url(url, decode_responses=True)
        # Ping to verify connection
        client.ping()
        return client
    except Exception as e:
        print(f"[Upstash Redis] Failed to connect: {e}")
        return None


def save_checkpoint(run_id: str, node_name: str, state_data: dict):
    """Save intermediate state data to Redis or memory fallback."""
    payload = json.dumps({
        "node_name": node_name,
        "state_data": state_data
    })
    
    client = get_redis_client()
    if client:
        try:
            # Save checkpoint with 24 hour expiry
            key = f"sentinelbrief:checkpoint:{run_id}"
            client.set(key, payload, ex=86400)
            print(f"[Upstash Redis] Checkpoint saved for run {run_id} at node '{node_name}'")
            return True
        except Exception as e:
            print(f"[Upstash Redis] Error saving checkpoint: {e}")
    
    # Fallback to local memory
    _in_memory_checkpoints[run_id] = {
        "node_name": node_name,
        "state_data": state_data
    }
    print(f"[Upstash Redis] Saved checkpoint {run_id}/{node_name} to In-Memory fallback.")
    return True


def get_checkpoint(run_id: str) -> dict:
    """Retrieve last successful checkpoint for run_id."""
    client = get_redis_client()
    if client:
        try:
            key = f"sentinelbrief:checkpoint:{run_id}"
            data = client.get(key)
            if data:
                parsed = json.loads(data)
                print(f"[Upstash Redis] Retrieved checkpoint for run {run_id} at node '{parsed['node_name']}'")
                return parsed
        except Exception as e:
            print(f"[Upstash Redis] Error fetching checkpoint: {e}")
            
    # Fallback
    checkpoint = _in_memory_checkpoints.get(run_id)
    if checkpoint:
        print(f"[Upstash Redis] Retrieved checkpoint {run_id} from In-Memory fallback.")
    return checkpoint


def clear_checkpoint(run_id: str):
    """Clear checkpoint on successful completion."""
    client = get_redis_client()
    if client:
        try:
            key = f"sentinelbrief:checkpoint:{run_id}"
            client.delete(key)
        except Exception as e:
            print(f"[Upstash Redis] Error deleting checkpoint: {e}")
            
    if run_id in _in_memory_checkpoints:
        del _in_memory_checkpoints[run_id]
