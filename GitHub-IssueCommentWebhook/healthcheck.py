import redis
import os
import sys

def check_redis_connection():
    """Check if Redis connection can be established."""
    try:
        redis_client = redis.Redis(
            host=os.environ['REDIS_HOST_URL'],
            username=os.environ['REDIS_USERNAME'],
            password=os.environ['REDIS_PASSWORD'],
            socket_connect_timeout=2
        )
        redis_client.ping()
        return True
    except redis.RedisError:
        return False

if __name__ == "__main__":
    if check_redis_connection():
        sys.exit(0)
    else:
        sys.exit(1)