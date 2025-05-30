from collections.abc import Callable, Iterable, Mapping
from datetime import timedelta
from typing import Any, Protocol, SupportsInt, TypeAlias, overload, type_check_only

from _typeshed import ReadableBuffer
from django.core.cache.backends.base import BaseCache
from redis._parsers import BaseParser
from redis.client import Redis
from redis.connection import ConnectionPool

@type_check_only
class _RedisCacheClientSerializer(Protocol):
    def dumps(self, obj: Any) -> bytes: ...
    @overload
    def loads(self, data: SupportsInt) -> int: ...
    @overload
    def loads(self, data: ReadableBuffer) -> Any: ...

class RedisSerializer:
    def __init__(self, protocol: int | None = None) -> None: ...
    def dumps(self, obj: Any) -> bytes: ...
    @overload
    def loads(self, data: SupportsInt) -> int: ...
    @overload
    def loads(self, data: ReadableBuffer) -> Any: ...

# Taken from https://github.com/redis/redis-py/blob/6b8978/redis/typing.py
_Key: TypeAlias = str | bytes | memoryview
_Expiry: TypeAlias = int | timedelta

class RedisCacheClient:
    def __init__(
        self,
        servers: list[str],
        serializer: str | Callable[[], _RedisCacheClientSerializer] | _RedisCacheClientSerializer | None = None,
        pool_class: str | type[ConnectionPool] | None = None,
        parser_class: str | type[BaseParser] | None = None,
        **options: Any,
    ) -> None: ...
    def get_client(self, key: _Key | None = None, *, write: bool = False) -> Redis: ...
    def add(self, key: _Key, value: Any, timeout: _Expiry | None) -> bool: ...
    def get(self, key: _Key, default: Any) -> Any: ...
    def set(self, key: _Key, value: Any, timeout: _Expiry | None) -> None: ...
    def touch(self, key: _Key, timeout: _Expiry) -> bool: ...
    def delete(self, key: _Key) -> bool: ...
    def get_many(self, keys: Iterable[_Key]) -> dict[_Key, Any]: ...
    def has_key(self, key: _Key) -> bool: ...
    def incr(self, key: _Key, delta: int) -> Any: ...
    def set_many(self, data: Mapping[_Key, Any], timeout: _Expiry) -> None: ...
    def delete_many(self, keys: Iterable[_Key]) -> None: ...
    def clear(self) -> bool: ...

class RedisCache(BaseCache):
    def __init__(self, server: str | list[str], params: dict[str, Any]) -> None: ...
