import datetime
import time

from django.test import TestCase
from django.conf import settings
from freezegun import freeze_time


def _get_cache(backend):
    try:
        # 1.9+
        from django.core.cache import caches
    except ImportError:
        # <1.9
        from django.core.cache import get_cache
        return get_cache(backend)
    return caches[backend]


class BaseCacheTestCase(TestCase):

    def setUp(self):
        self.cache = _get_cache(self.cache_name)

    def key(self, key):
        return u'ft-cache-test:{cache}:{key}'.format(key=key,
                                                     cache=self.cache_name)

    def seconds_in_the_past(self, seconds):
        return freeze_time(datetime.datetime.utcnow() -
                           datetime.timedelta(seconds=seconds))


class WorkingCacheTests(BaseCacheTestCase):
    cache_name = 'default'

    def test_basics(self):
        """Sanity check that things still work as expected"""
        key = self.key('basics')
        val = 'value'
        self.cache.delete(key)
        self.cache.set(key, val)
        self.assertEqual(self.cache.get(key), val)

    def test_overflow(self):
        """Inserting past 1MB limit should not raise error"""
        key = self.key('big')
        blob = '0' * 1048576
        self.cache.set(key, blob)
        self.assertEqual(self.cache.get(key), None)


class BadCacheTests(BaseCacheTestCase):
    cache_name = 'faulty'

    def test_basics(self):
        """Cache should fail, log traceback, but not raise error"""
        key = self.key('basics')
        val = 'value'
        self.cache.delete(key)
        self.cache.set(key, val)
        self.assertEqual(self.cache.get(key), None)


class MintCacheTests(BaseCacheTestCase):
    cache_name = 'mint'
    ttl = 20

    def test_still_in_cache(self):
        key = self.key('still-in-cache')
        val = 'value'
        with self.seconds_in_the_past(self.ttl + 5):
            self.cache.set(key, val, self.ttl)
        ret_val = self.cache.get(key)
        # cache miss
        self.assertIsNone(ret_val)
        ret_val = self.cache.get(key)
        # herd hit
        self.assertEqual(ret_val, val)

    def test_get(self):
        key = self.key('get')
        val = 'value'
        self.cache.set(key, val, self.ttl)
        self.assertEqual(self.cache.get(key), val)

    def test_add(self):
        key = self.key('add')
        val = 'value'
        self.cache.add(key, val, self.ttl)
        self.assertEqual(self.cache.get(key), val)

    def test_herd_expired(self):
        key_set = self.key('set-expired')
        key_add = self.key('add-expired')
        val = 'value'
        with self.seconds_in_the_past(self.ttl + 5):
            self.cache.set(key_set, val, self.ttl)
            self.cache.add(key_add, val, self.ttl)
        ret_val_set = self.cache.get(key_set)
        ret_val_add = self.cache.get(key_add)
        # Expect a cache miss
        self.assertIsNone(ret_val_set)
        self.assertIsNone(ret_val_add)
        # TODO: figure out how to pass herd timeout without sleeping
        time.sleep(settings.CACHE_HERD_TIMEOUT + 0.1)
        ret_val_set = self.cache.get(key_set)
        ret_val_add = self.cache.get(key_add)
        # Expect herd timeout expired and cache miss
        self.assertIsNone(ret_val_set)
        self.assertIsNone(ret_val_add)

    def test_not_expired(self):
        key = self.key('not-expired')
        val = 'no'
        with self.seconds_in_the_past(self.ttl / 2):
            self.cache.set(key, val, self.ttl)
        ret_val = self.cache.get(key)
        self.assertEqual(ret_val, val)

    def test_get_many(self):
        data = [
            (self.key('get-many-a'), 'b'),
            (self.key('get-many-c'), 'd'),
            (self.key('get-many-e'), 'f'),
        ]
        with self.seconds_in_the_past(self.ttl + 5):
            self.cache.set(*data[0], timeout=1)
            self.cache.set(*data[1], timeout=self.ttl)
            self.cache.set(*data[2], timeout=self.ttl * 10)
        results = self.cache.get_many([d[0] for d in data])
        self.assertIsNone(results[data[0][0]])
        self.assertIsNone(results[data[1][0]])
        self.assertIn(data[2], results.items())

    def test_set_many(self):
        data = [
            (self.key('set-many-a'), 'b'),
            (self.key('set-many-c'), 'd'),
            (self.key('set-many-e'), 'f'),
        ]
        with self.seconds_in_the_past(self.ttl + 5):
            self.cache.set_many(dict(data), self.ttl)
        results = self.cache.get_many([d[0] for d in data])
        for v in results.values():
            self.assertIsNone(v)
        results = self.cache.get_many([d[0] for d in data])
        for k, v in results.items():
            self.assertEqual(dict(data)[k], v)

    def test_false_marker(self):
        key = self.key('false-marker')
        value = ('a', 'false', 'marker')
        self.cache.set(key, value, self.ttl, herd=False)
        self.assertEqual(self.cache.get(key), value)


class FTMintWorkingCacheTests(WorkingCacheTests):
    cache_name = 'ft-mint'


class FTMintBadCacheTests(BadCacheTests):
    cache_name = 'ft-mint-faulty'


class FTMintCacheTests(MintCacheTests):
    cache_name = 'ft-mint'
