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

__version__ = '0.0.5'


class FilenameMarker(object):
	"""Marker for filenames.

	Many methods if :py:class:`Cache` take a key that identifies a cache item.
	This key is converted to a file path by :py:meth:`Cache._path` by creating
	a hash of the key and appending it to :py:attr:`Cache.dir_name`.

	Unfortunately, the original key is available in :py:meth:`Cache.__iter__`.
	Three solutions come to mind:

	1.  Keep a separate list of all keys
	2.  Store the key with each cache item
	3.  Allow to also pass the filename to :py:meth`Cache._path`

	This is used to implement the last option by providing a way to distinguish
	between regular keys and filenames. Keys therefore must not be instances of
	this class.

	"""
	def __init__(self, value):
		self.value = value


class BaseCache(object):
	def __init__(self, maxsize, ttl=None, missing=None):
		self.maxsize = maxsize
		self.ttl = ttl
		self.missing = missing

	def values(self):
		return [self[key] for key in self]

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

	def expire(self):
		"""Delete items based on TTL."""
		if self.ttl is not None:
			threshold = time() - self.ttl

			for key in self:
				if self.mtime(key) < threshold:
					del self[key]

	def clear(self):
		"""Delete items with lowest weight until cache fits maxsize."""
		self.expire()
		while self.currsize > self.maxsize:
			key = min(self, key=self.getweightof)
			del self[key]


class Cache(BaseCache):
	def __init__(self, name, maxsize, ttl=None, missing=None):
		BaseCache.__init__(self, maxsize, ttl=ttl, missing=missing)
		self.name = name
		self.dir_name = os.path.join(CACHE_DIR, name)

		if not os.path.exists(self.dir_name):
			os.makedirs(self.dir_name)

	def _path(self, key):
		if isinstance(key, FilenameMarker):
			filename = key.value
		else:
			filename = str(hash(key))
		return os.path.join(self.dir_name, filename)

	def __getitem__(self, key):
		path = self._path(key)
		if key in self:
			with open(path) as fh:
				return pickle.load(fh)
		else:
			raise KeyError(key)

	def __setitem__(self, key, value):
		path = self._path(key)
		with open(path, 'w') as fh:
			pickle.dump(value, fh)
		self.clear()

	def __delitem__(self, key):
		if key in self:
			path = self._path(key)
			os.unlink(path)
		else:
			raise KeyError(key)

	def __contains__(self, key):
		path = self._path(key)
		return os.path.exists(path)

	def __iter__(self):
		for filename in os.listdir(self.dir_name):
			yield FilenameMarker(filename)

	def getatimeof(self, key):
		if key in self:
			path = self._path(key)
			return os.path.getatime(path)
		else:
			raise KeyError(key)

	def getmtimeof(self, key):
		if key in self:
			path = self._path(key)
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
	'Cache',
	'LRUCache',
	'cachedmethod',
	'lru_cache',
	'ttl_cache',
)
