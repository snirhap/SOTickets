import redis
from app import logging
from app.static.exceptions import KeyNotFound

logger = logging.getLogger()

class RedisManager:
    def __init__(self, host = 'localhost', port = '6379') -> None:
        self.__redis_manager = redis.Redis(host, port, decode_responses=True)

    def set_key_value(self, key, value, exp_sec = None):
        self.__redis_manager.set(name=key, value=value, ex=exp_sec)

    def get_value_by_key(self, key):
        if self.__redis_manager.exists(key):
            value = self.__redis_manager.get(key)
            return value
        else:
            return None

    def delete_key(self, key):
        if self.__redis_manager.exists(key):
            self.__redis_manager.delete(key)
        else:
            raise KeyNotFound(f"Couldn't delete Key {key} because it does not exist in DB")

    def hset_key_value(self, key, value, exp_sec):
        self.__redis_manager.hset(key, mapping=value)
        self.__redis_manager.expire(key, exp_sec)

    def hgetall_key(self, key):
        if self.__redis_manager.exists(key):
            return self.__redis_manager.hgetall(key)
        else:
            raise KeyNotFound(f"{key} because it does not exist in DB")
    
    def scan_within_pattern(self, pattern: str, count: int = None):
        keys = []
        try:
            result = self.__redis_manager.scan_iter(match=pattern, count=count)
            for elem in result:
                keys.append(elem)
            return keys
        except Exception as err:
            logger.error(err)

    def lpush_key_value(self, key, values, exp_sec=None):
        self.__redis_manager.lpush(key, *values)
        self.__redis_manager.expire(key, exp_sec)

    def lrange_key(self, key):
        if self.__redis_manager.exists(key):
            return self.__redis_manager.lrange(key, 0, -1)
        else:
            raise KeyNotFound(f"{key} because it does not exist in DB")
