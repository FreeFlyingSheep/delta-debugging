from typing import Any, Sequence

from delta_debugging import Configuration, Debugger, DDMin, Input, Outcome, TreeCache


def oracle(config: Configuration) -> Outcome:
    data: Sequence[Any] = config.data
    outcome: Outcome = Outcome.PASS
    if 5 not in data:
        outcome = Outcome.UNRESOLVED
    elif 3 in data and 7 in data:
        outcome = Outcome.FAIL
    return outcome


def main() -> None:
    input: Input = Input(list(range(10)))
    cache: TreeCache = TreeCache()
    debugger: Debugger = Debugger(DDMin(), oracle, cache=cache)
    debugger.debug(input)
    print(debugger.to_string())
    print(cache.to_string())
    print(debugger.result)


if __name__ == "__main__":
    main()
