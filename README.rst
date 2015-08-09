filecachetools - cachetools compatible persistent cache::

    from filecachetools import lru_cache

    @lru_cache('complex_computation')
    def complex_comptation(a, b):
        return a + b

This example will create a directory ``~/.cache/complex_comptation/``
where it will create a cache file for each set of arguments to the
function. This way, the cache will persist accross runs of the program.
