0.2.0
-----

-   Adapt to changes in cachetools 1.1.0.  The only API change
    is that ``lru_cache`` and ``ttl_cache`` no lonbger accept
    the ``typed`` argument.

0.1.2
-----

-   Adapt to internal changes in cachetools


0.1.1
-----

-   Raise less KeyErrors on parallel execution.


0.1.0
-----

-   Delete outdated cache items on get, not only when
    :py:func:`expire` is called.

-   :py:func:`clear` now actually removes all items from the
    cache instead of only removing outdated ones and limiting
    to :py:obj:`maxsize`.

-   Added python3 support.  Note that this only means that
    the library works with both python2 and python3.  There
    are no tests for using the same cached items with both.
    See also http://bugs.python.org/issue6137.

-   Fix: :py:func:`getatimeof` did report the time of the last
    get instead of the time of the last get *or* set.


0.0.7
-----

-   Another fix to ttl expiry


0.0.6
-----

-   Fix: :py:obj:`ttl` was not properly passed to the base
    constructor so that old items were not removed after the
    specified time.


0.0.5
-----

-   Fix: :py:mod:`setup.py` imported :py:mod:`filecachetools`
    causing an :py:exc:`ImportError` when :py:mod:`cachetools`
    was not installed.


0.0.4
-----

-   Fix: atime was changed on overy call to :py:func:`__iter__`
    causing unexpected behavior on :py:class:`LRUCache`.


0.0.3
-----

-   provide :py:meth:`Cache.clear`


0.0.2
-----

-   Fix: Valid filenames


0.0.1
-----

-   Fix installation issue.


0.0.0
-----

initial release
