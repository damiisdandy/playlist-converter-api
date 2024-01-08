import redis


def create_redis():
    return redis.Redis(host='localhost', port=6379, db=0, username=None, password=None)
