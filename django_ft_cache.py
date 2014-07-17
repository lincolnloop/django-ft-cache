import logging
from functools import wraps

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


class FaultTolerantCacheMixin(object):
    """
    Wraps memcache client methods allowing them to fail
    without raising an exception.
    """
    methods_to_patch = ('get', 'set', 'incr', 'decr', 'delete',
                        'get_multi', 'set_multi', 'delete_multi')

    @property
    def _cache(self):
        """
        Implements transparent thread-safe access to a memcached client.
        """
        if getattr(self, '_client', None) is None:
            self._client = self._lib.Client(self._servers)
            for name in self.methods_to_patch:
                method = fault_tolerant_wrapper(getattr(self._client, name))
                setattr(self._client, name, method)
        return self._client


class FaultTolerantPyLibMCCache(FaultTolerantCacheMixin, PyLibMCCache):
    pass
