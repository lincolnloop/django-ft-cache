from itertools import repeat
from django.test import TestCase
from django.core.cache import get_cache


class BaseCacheTestCase(TestCase):

    def setUp(self):
        self.cache = get_cache(self.cache_name)

    def key(self, key):
        return u'ft-cache-test:{cache}:{key}'.format(key=key,
                                                     cache=self.cache_name)


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
