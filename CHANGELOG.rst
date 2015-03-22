Changelog
=========

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
