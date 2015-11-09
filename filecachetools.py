"""cachetools compatible persistent cache.

This module provides various memoizing collections and decorators, similar to
`cachetools <https://github.com/tkem/cachetools>`_.  But instead of saving
cache items in memory, they are pickled to a subdirectory of ``~/.cache/``.
"""

from time import time
import os
import pickle

from cachetools import cached
from cachetools import cachedmethod  # noqa

CACHE_DIR = '~/.cache/'
MARKER = object()

__version__ = '0.2.0'


class FilenameMarker(object):
	"""Marker for filenames.

	Many methods if :py:class:`Cache` take a key that identifies a cache item.
	This key is converted to a file path by :py:meth:`Cache._path` by creating
	a hash of the key and appending it to :py:attr:`Cache.dir_name`.

	Unfortunately, the original key is unavailable in :py:meth:`Cache.__iter__`.
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
		"""Return a list of all cached values."""
		return [self[key] for key in self]

	@property
	def currsize(self):
		"""The accumulated size of all cached values."""
		return sum(map(self.getsizeof, self))

	def get(self, key, default=None):
		"""Return a cached value."""
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
		"""Return or initialize a cached value.

		If the key does not yet exist in the cache, it is created with value
		`default`. Always returns the cached value.

		"""
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

	def _is_fresh(self, key):
		if self.ttl is None:
			return True
		else:
			return self.getmtimeof(key) >= time() - self.ttl

	def expire(self):
		"""Delete items based on TTL."""
		if self.ttl is not None:
			for key in self:
				try:
					if not self._is_fresh(key):
						del self[key]
				except KeyError:
					pass

	def limit(self):
		"""Delete items with lowest weight until cache fits maxsize."""
		self.expire()
		while self.currsize > self.maxsize:
			key = min(self, key=self.getweightof)
			try:
				del self[key]
			except KeyError:
				pass

	def clear(self):
		"""Delete all items."""
		keys = list(self)

		for key in keys:
			try:
				del self[key]
			except KeyError:
				pass

	def __getitem__(self, key):  # pragma: nocover
		raise NotImplementedError

	def __setitem__(self, key, value):  # pragma: nocover
		raise NotImplementedError

	def __delitem__(self, key):  # pragma: nocover
		raise NotImplementedError

	def __contains__(self, key):  # pragma: nocover
		raise NotImplementedError

	def __iter__(self, key):  # pragma: nocover
		raise NotImplementedError

	def getmtimeof(self, key):  # pragma: nocover
		raise NotImplementedError

	def getweightof(self, key):  # pragma: nocover
		raise NotImplementedError


class Cache(BaseCache):
	"""Mutable mapping to serve as a simple cache or cache base class."""
	def __init__(self, name, maxsize,
			ttl=None, missing=None, protocol=None, base_dir=CACHE_DIR):
		BaseCache.__init__(self, maxsize, ttl=ttl, missing=missing)
		self.protocol = protocol
		self.name = name
		self.dir_name = os.path.join(os.path.expanduser(base_dir), name)

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
			if self._is_fresh(key):
				with open(path, 'rb') as fh:
					return pickle.load(fh)
			else:
				del self[key]
		raise KeyError(key)

	def __setitem__(self, key, value):
		path = self._path(key)
		with open(path, 'wb') as fh:
			pickle.dump(value, fh, protocol=self.protocol)
		self.limit()

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
		"""Return the last access time of a cache item."""
		if key in self:
			path = self._path(key)
			mtime = os.path.getmtime(path)
			atime = os.path.getatime(path)
			return max(atime, mtime)
		else:
			raise KeyError(key)

	def getmtimeof(self, key):
		"""Return the last modification time of a cache item."""
		if key in self:
			path = self._path(key)
			return os.path.getmtime(path)
		else:
			raise KeyError(key)

	def getsizeof(self, key):
		"""Return the size of a cache item's value."""
		if key in self:
			return 1
		else:
			raise KeyError(key)

	def getweightof(self, key):
		"""Return the "weight" of a cache item.

		Items with lower weight will be removed from the cache first.

		"""
		return self.getmtimeof(key)


class LRUCache(Cache):
	"""Least Recently Used (LRU) cache implementation.

	This class discards the least recently used items first to make space
	when necessary.

	"""
	def getweightof(self, key):
		return self.getatimeof(key)


def lru_cache(name, maxsize=128, ttl=None):  # pragma: nocover
	"""Decorator to wrap a function with a memoizing callable that saves
	up to `maxsize` results based on a Least Recently Used (LRU)
	algorithm.

	"""
	return cached(LRUCache(name, maxsize, ttl=ttl))


def ttl_cache(name, maxsize=128, ttl=600):  # pragma: nocover
	"""Decorator to wrap a function with a memoizing callable that saves
	up to `maxsize` results based on a per-item time-to-live (TTL) value.

	"""
	return cached(Cache(name, maxsize, ttl=ttl))


__all__ = (
	'Cache',
	'LRUCache',
	'cachedmethod',
	'lru_cache',
	'ttl_cache',
)
