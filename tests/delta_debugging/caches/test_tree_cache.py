import doctest

from delta_debugging import Configuration, Outcome, TreeCache


def test_tree() -> None:
    cache: TreeCache = TreeCache()
    config1: Configuration = [1, 2, 3]
    cache[config1] = Outcome.FAIL
    assert cache[config1] == Outcome.FAIL
    assert config1 in cache
    config2: Configuration = [0]
    assert config2 not in cache
    cache[config2] = Outcome.PASS
    assert config2 in cache
    print(cache.to_string())
    assert cache[config2] == Outcome.PASS
    cache.clear()
    print(cache.to_string())
    assert config1 not in cache
    assert config2 not in cache


def test_docstring() -> None:
    import delta_debugging.caches.tree

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.caches.tree, verbose=True
    )
    assert results.failed == 0
