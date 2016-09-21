import logging
from functools import wraps

from django.utils.functional import cached_property
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

    @cached_property
    def _cache(self):
        # existing Django code
        client = self._lib.Client(self._servers)
        if self._options:
            client.behaviors = self._options
        # overrides
        for name in self.methods_to_patch:
                method = fault_tolerant_wrapper(getattr(client, name))
                setattr(client, name, method)
        return client


class FaultTolerantPyLibMCCache(FaultTolerantCacheMixin, PyLibMCCache):
    pass
