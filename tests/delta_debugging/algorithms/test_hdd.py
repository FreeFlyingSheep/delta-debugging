import doctest

from delta_debugging import (
    Configuration,
    DDMin,
    Debugger,
    HDD,
    Outcome,
    ProbDD,
    TreeSitterParser,
)


def oracle(config: Configuration) -> Outcome:
    try:
        data: bytes = bytes(config)
        print(data)
        exec(data)
    except ZeroDivisionError:
        return Outcome.FAIL
    except Exception:
        return Outcome.UNRESOLVED
    return Outcome.PASS


def test_hdd() -> None:
    parser = TreeSitterParser("python", expand_whitespace=True)
    source: bytes = """
x = 1
y = 0

def f(x):
    return x / 0

def g(x):
    return x * 2

z = f(x)
print(g(z))
""".encode("utf8")
    expected: bytes = b"x = 1\ndef f(x):\nreturn x / 0\nz = f(x)\n"
    debugger: Debugger = Debugger(HDD(parser, DDMin()), oracle)
    result: Configuration = debugger.debug(list(source))
    print(debugger.to_string())
    assert bytes(result) == expected

    debugger: Debugger = Debugger(HDD(parser, ProbDD()), oracle)
    result: Configuration = debugger.debug(list(source))
    print(debugger.to_string())
    assert bytes(result) == expected


def test_docstring() -> None:
    import delta_debugging.algorithms.hdd

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.algorithms.hdd, verbose=True
    )
    assert results.failed == 0
