import unittest
from random import randint
from shutil import rmtree
from time import sleep
import os

import filecachetools


class TestFilenameMarker(unittest.TestCase):
    def test_distinguishable_from_string(self):
        s = 'foo'
        fm = filecachetools.FilenameMarker(s)
        self.assertNotEqual(s, fm)
        self.assertIsInstance(fm, filecachetools.FilenameMarker)
        self.assertNotIsInstance(s, filecachetools.FilenameMarker)


class TestCacheBase(unittest.TestCase):
    cache_class = filecachetools.Cache

    def setUp(self):
        self.base_dir = '/tmp/cache-%i' % randint(1000, 10000)

    def tearDown(self):
        rmtree(self.base_dir)


class TestBaseCache(TestCacheBase):
    def test_dir_exists(self):
        os.makedirs(os.path.join(self.base_dir, 'test'))
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value'
        self.assertEqual(cache['key'], 'value')

    def test_values(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key1'] = 'value1'
        cache['key2'] = 'value2'
        self.assertSetEqual(set(cache.values()), set(['value1', 'value2']))

    def test_get(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value'
        self.assertEqual(cache.get('key'), 'value')

    def test_get_missing(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        self.assertIsNone(cache.get('missing'))

    def test_get_default(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value'
        self.assertEqual(cache.get('key', 'default'), 'value')

    def test_get_missing_default(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        default = 'huhu'
        self.assertEqual(cache.get('missing', default), default)

    def test_pop(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value'
        self.assertEqual(cache.pop('key'), 'value')
        self.assertFalse('key' in cache)

    def test_pop_missing(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        with self.assertRaises(KeyError):
            cache.pop('key')

    def test_pop_default(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value'
        self.assertEqual(cache.pop('key', 'default'), 'value')
        self.assertFalse('key' in cache)

    def test_pop_missing_default(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        self.assertEqual(cache.pop('key', 'default'), 'default')

    def test_setdefault(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value'
        self.assertEqual(cache.setdefault('key'), 'value')
        self.assertEqual(cache['key'], 'value')

    def test_setdefault_missing(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        self.assertIsNone(cache.setdefault('key'))
        self.assertIsNone(cache['key'])

    def test_setdefault_default(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value'
        self.assertEqual(cache.setdefault('key', 'default'), 'value')
        self.assertEqual(cache['key'], 'value')

    def test_setdefault_default_missing(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        self.assertEqual(cache.setdefault('key', 'default'), 'default')
        self.assertEqual(cache['key'], 'default')

    def test_missing(self):
        args = []

        def fn(key):
            args.append(key)
            return 'value'

        cache = self.cache_class(
            'test', 1000, base_dir=self.base_dir, missing=fn)
        self.assertEqual(cache.__missing__('key'), 'value')
        self.assertEqual(cache['key'], 'value')
        self.assertEqual(args, ['key'])

    def test_missing_missing(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        with self.assertRaises(KeyError):
            cache.__missing__('key')

    def test_expire(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir, ttl=1)
        cache['key1'] = 'value1'
        sleep(2)
        cache['key2'] = 'value2'  # calls expire automatically
        self.assertSetEqual(set(cache.values()), set(['value2']))

    def test_clear(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key1'] = 'value1'
        cache['key2'] = 'value2'
        cache.clear()
        self.assertEqual(len(cache.values()), 0)


class TestCache(TestCacheBase):
    def test_get_missing(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        with self.assertRaises(KeyError):
            cache['missing']

    def test_set_and_get(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value'
        self.assertEqual(cache['key'], 'value')

    def test_set_and_get_multiple(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key1'] = 'value1'
        cache['key2'] = 'value2'
        self.assertEqual(cache['key1'], 'value1')
        self.assertEqual(cache['key2'], 'value2')

    def test_override(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value1'
        cache['key'] = 'value2'
        self.assertEqual(cache['key'], 'value2')

    def test_delete(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value1'
        del cache['key']
        with self.assertRaises(KeyError):
            cache['key']

    def test_delete_missing(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        with self.assertRaises(KeyError):
            del cache['key']

    def test_get_expired(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir, ttl=1)
        cache['key'] = 'value'
        sleep(2)
        with self.assertRaises(KeyError):
            cache['key']

    def test_limit(self):
        cache = self.cache_class('test', 2, base_dir=self.base_dir)
        cache['key1'] = 'value1'
        cache['key2'] = 'value2'
        cache['key3'] = 'value3'
        self.assertEqual(len(cache.values()), 2)

    def test_missing_atime(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        with self.assertRaises(KeyError):
            cache.getatimeof('missing')

    def test_atime_increases_on_get(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value'
        atime1 = cache.getatimeof('key')
        sleep(0.1)
        cache['key']
        atime2 = cache.getatimeof('key')
        self.assertLess(atime1, atime2)

    def test_atime_increases_on_set(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value1'
        atime1 = cache.getatimeof('key')
        sleep(0.1)
        cache['key'] = 'value2'
        atime2 = cache.getatimeof('key')
        self.assertLess(atime1, atime2)

    def test_atime_not_increases_on_meta(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value1'
        atime1 = cache.getatimeof('key')
        sleep(0.1)
        cache.getatimeof('key')
        cache.getmtimeof('key')
        cache.getsizeof('key')
        atime2 = cache.getatimeof('key')
        self.assertEqual(atime1, atime2)

    def test_missing_mtime(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        with self.assertRaises(KeyError):
            cache.getmtimeof('missing')

    def test_mtime_not_increases_on_get(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value'
        mtime1 = cache.getmtimeof('key')
        sleep(0.1)
        cache['key']
        mtime2 = cache.getmtimeof('key')
        self.assertEqual(mtime1, mtime2)

    def test_mtime_increases_on_set(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value1'
        mtime1 = cache.getmtimeof('key')
        sleep(0.1)
        cache['key'] = 'value2'
        mtime2 = cache.getmtimeof('key')
        self.assertLess(mtime1, mtime2)

    def test_mtime_not_increases_on_meta(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        cache['key'] = 'value1'
        mtime1 = cache.getmtimeof('key')
        sleep(0.1)
        cache.getmtimeof('key')
        cache.getmtimeof('key')
        cache.getsizeof('key')
        mtime2 = cache.getmtimeof('key')
        self.assertEqual(mtime1, mtime2)

    def test_missing_size(self):
        cache = self.cache_class('test', 1000, base_dir=self.base_dir)
        with self.assertRaises(KeyError):
            cache.getsizeof('missing')


class TestLRUCache(TestCache):
    cache_class = filecachetools.LRUCache
