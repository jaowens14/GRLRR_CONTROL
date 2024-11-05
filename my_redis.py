import redis

class MyRedis():
    def __init__(self: redis.Redis):
        self.r = redis.Redis()