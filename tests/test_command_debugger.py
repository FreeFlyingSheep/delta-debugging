import doctest
from subprocess import CompletedProcess

from delta_debugging import (
    CommandDebugger,
    Configuration,
    DDMin,
    HashCache,
    Outcome,
)


def my_check(result: CompletedProcess) -> Outcome:
    print(result.args)
    if result.returncode != 0:
        return Outcome.UNRESOLVED
    if b".." in result.stdout:
        return Outcome.FAIL
    return Outcome.PASS


def pre_check(config: Configuration, command: list[str]) -> None:
    command.extend(config)


def test_command() -> None:
    command: list[str] = ["ls"]
    options: list[str] = ["-l", "-a", "-h"]
    algorithm: DDMin = DDMin()
    cache: HashCache = HashCache()
    debugger: CommandDebugger = CommandDebugger(
        algorithm, command, my_check, cache=cache, pre_check=pre_check
    )
    result: Configuration = debugger.debug(options)
    print(cache.to_string())
    assert result == ["-a"]


def test_docstring() -> None:
    import delta_debugging.debuggers.command

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.debuggers.command, verbose=True
    )
    assert results.failed == 0
