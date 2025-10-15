from delta_debugging import Configuration, Debugger, DDMin, Outcome, TreeCache


def oracle(config: Configuration) -> Outcome:
    outcome: Outcome = Outcome.PASS
    if 5 not in config:
        outcome = Outcome.UNRESOLVED
    elif 3 in config and 7 in config:
        outcome = Outcome.FAIL
    return outcome


def main() -> None:
    cache: TreeCache = TreeCache()
    debugger: Debugger = Debugger(DDMin(), oracle, cache=cache)
    debugger.debug(list(range(10)))
    print(debugger.to_string())
    print(cache.to_string())
    print(debugger.result)


if __name__ == "__main__":
    main()
