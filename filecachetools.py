"""cachetools compatible persistent cache.

This module provides various memoizing collections and decorators, similar to
`cachetools <https://github.com/tkem/cachetools>`_.  But instead of saving
cache items in memory, they are pickled to a subdirectory of ``~/.cache/``.
"""

from time import time
import os
import pickle

from cachetools.decorators import cachedfunc
from cachetools.decorators import cachedmethod  # noqa

CACHE_DIR = os.path.expanduser('~/.cache/')
MARKER = object()


class BaseCache(object):
	def __init__(self, maxsize, ttl=None, missing=None):
		self.maxsize = maxsize
		self.ttl = ttl
		self.missing = missing

	def values(self):
		return [self[key] for key in self]

	def items(self):
		return [(key, self[key]) for key in self]

	@property
	def currsize(self):
		return sum(map(self.getsizeof, self))

	def get(self, key, default=None):
		if key in self:
			return self[key]
		else:
			return default

	def pop(self, key, default=MARKER):
		if key in self:
			value = self[key]
			del self[key]
			return value
		elif default is MARKER:
			raise KeyError(key)
		else:
			return default

	def setdefault(self, key, default=None):
		if key not in self:
			self[key] = default
		return self[key]

	def __missing__(self, key):
		if self.missing:
			value = self.missing(key)
			self[key] = value
			return value
		else:
			raise KeyError(key)


class Cache(BaseCache):
	def __init__(self, name, maxsize, ttl=None, missing=None):
		BaseCache.__init__(self, maxsize, missing)
		self.name = name
		self.dir_name = os.path.join(CACHE_DIR, name)

		if not os.path.exists(self.dir_name):
			os.makedirs(self.dir_name)

	def __getitem__(self, key):
		if key in self:
			path = os.path.join(self.dir_name, key)
			with open(path) as fh:
				return pickle.load(fh)
		else:
			raise KeyError(key)

	def __setitem__(self, key, value):
		path = os.path.join(self.dir_name, key)
		with open(path, 'w') as fh:
			pickle.dump(value, fh)
		self.limit()

	def __delitem__(self, key):
		if key in self:
			path = os.path.join(self.dir_name, key)
			os.unlink(path)
		else:
			raise KeyError(key)

	def __contains__(self, key):
		path = os.path.join(self.dir_name, key)
		return os.path.exists(path)

	def keys(self):
		return os.listdir(self.dir_name)

	def __iter__(self):
		for key in self.keys():
			yield key

	def getatimeof(self, key):
		if key in self:
			path = os.path.join(self.dir_name, key)
			return os.path.getatime(path)
		else:
			raise KeyError(key)

	def getmtimeof(self, key):
		if key in self:
			path = os.path.join(self.dir_name, key)
			return os.path.getmtime(path)
		else:
			raise KeyError(key)

	def getsizeof(self, key):
		if key in self:
			return 1
		else:
			raise KeyError(key)

	def getweightof(self, key):
		return self.getmtimeof(key)

	def expire(self):
		"""Delete items based on TTL."""
		if self.ttl is not None:
			threshold = time() - self.ttl

			for key in self:
				if self.mtime(key) < threshold:
					del self[key]

	def limit(self):
		"""Delete items with lowest weight until cache fits maxsize."""
		self.expire()
		while self.currsize > self.maxsize:
			key = min(self, key=self.getweightof)
			del self[key]


class LRUCache(Cache):
	def getweightof(self, key):
		return self.getatimeof(key)


def lru_cache(name, maxsize=128, ttl=None, typed=False):
	"""Decorator to wrap a function with a memoizing callable that saves
	up to `maxsize` results based on a Least Recently Used (LRU)
	algorithm.

	"""
	return cachedfunc(LRUCache(name, maxsize, ttl=ttl), typed)


def ttl_cache(name, maxsize=128, ttl=600, typed=False):
	"""Decorator to wrap a function with a memoizing callable that saves
	up to `maxsize` results based on a per-item time-to-live (TTL) value.

	"""
	return cachedfunc(Cache(name, maxsize, ttl=ttl), typed)

__all__ = (
    'Cache', 'LRUCache',
    'cachedmethod',
    'lru_cache', 'ttl_cache',
)
