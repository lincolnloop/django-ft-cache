import logging
from functools import wraps

import time
from django.conf import settings
from django.utils.functional import cached_property
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache.backends.memcached import PyLibMCCache

logger = logging.getLogger(__name__)


def fault_tolerant_wrapper(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
        except Exception as err:
            logger.error(u"cache.%s failed with args: %s", f.__name__, args)
            logger.exception(err)
            result = None
        return result
    return wrapper


class Marker(object):
    pass


MARKER = Marker()


class MintCacheMixin(object):
    """Thundering herd mitigation"""
    herd_timeout = getattr(settings, 'CACHE_HERD_TIMEOUT', 60)

    def _pack_value(self, value, timeout):
        """
        Packs a value to include a marker (to indicate that it's a packed
        value), the value itself, and the value's timeout information.
        """
        timeout_time = timeout + int(time.time())
        return MARKER, value, timeout_time

    def _unpack_value(self, value, default=None):
        """
        Unpacks a value and returns a tuple whose first element is the value,
        and whose second element is whether it needs to be herd refreshed.
        """
        try:
            marker, unpacked, original_timeout = value
        except (ValueError, TypeError):
            return value, False
        if not isinstance(marker, Marker):
            return value, False
        if original_timeout < int(time.time()):
            return unpacked, True
        return unpacked, False

    def add(self, key, value, timeout=None, version=None):
        original_timeout = self.get_backend_timeout(timeout)
        value = self._pack_value(value, original_timeout)
        timeout = original_timeout + self.herd_timeout
        return super(MintCacheMixin, self).add(key, value, timeout, version)

    def get(self, key, default=None, version=None):
        packed_val = super(MintCacheMixin, self).get(key, default, version)
        val, refresh = self._unpack_value(packed_val)
        # If the cache has expired according to the embedded timeout, then
        # shove it back into the cache for a while, but act as if it was a
        # cache miss.
        if refresh:
            self.set(key, val, self.get_backend_timeout(self.herd_timeout),
                     herd=False)
            return default

        return val

    def set(self, key, value, timeout=None, version=None, herd=True):
        # pack value with original timeout
        original_timeout = self.get_backend_timeout(timeout)
        if herd and original_timeout > 0:
            timeout = original_timeout + self.herd_timeout
            value = self._pack_value(value, original_timeout)
        super(MintCacheMixin, self).set(key, value, timeout, version)

    def get_many(self, keys, version=None):
        packed_ret = super(MintCacheMixin, self).get_many(keys, version)
        to_reinsert = {}
        to_return = {}
        for key, packed in packed_ret.items():
            val, refresh = self._unpack_value(packed)
            if refresh:
                to_reinsert[key] = val
                val = None
            to_return[key] = val

        if to_reinsert:
            self.set_many(to_reinsert,
                           self.herd_timeout,
                           herd=False)
        return to_return

    def set_many(self, data, timeout=DEFAULT_TIMEOUT, version=None, herd=True):
        original_timeout = self.get_backend_timeout(timeout)
        if herd and original_timeout > 0:
            timeout = original_timeout + self.herd_timeout
            data = {k: self._pack_value(v, original_timeout)
                    for k, v in data.items()}

        super(MintCacheMixin, self).set_many(data, timeout, version)


class FaultTolerantCacheMixin(object):
    """
    Wraps memcache client methods allowing them to fail
    without raising an exception.
    """
    methods_to_patch = ('get', 'set', 'incr', 'decr', 'delete',
                        'get_multi', 'set_multi', 'delete_multi')

    @cached_property
    def _cache(self):
        client = super(FaultTolerantCacheMixin, self)._cache
        for name in self.methods_to_patch:
                method = fault_tolerant_wrapper(getattr(client, name))
                setattr(client, name, method)
        return client


class FaultTolerantPyLibMCCache(FaultTolerantCacheMixin, PyLibMCCache):
    pass


class PyLibMCMintCache(MintCacheMixin, PyLibMCCache):
    pass


class FaultTolerantPyLibMCMintCache(MintCacheMixin,
                                    FaultTolerantCacheMixin,
                                    PyLibMCCache):
    pass
