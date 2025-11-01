import os
from dataclasses import dataclass

from matplotlib import pyplot as plt

from delta_debugging import ResultCollection


@dataclass(frozen=True)
class DrawArgs:
    metric: str
    title: str | None = None
    log: bool = False
    group_file: bool = True


def draw(file: str | os.PathLike) -> None:
    results = ResultCollection()
    results.load_results(file)

    args: list[DrawArgs] = [
        DrawArgs(
            metric="Reduction Ratio",
            title="Reduction Ratio by File and Algorithm",
        ),
        DrawArgs(metric="Count", title="Oracle Calls by File and Algorithm", log=True),
        DrawArgs(metric="Time", title="Execution Time by File and Algorithm", log=True),
        DrawArgs(
            metric="Reduction Ratio",
            title="Mean Reduction Ratio per Algorithm",
            group_file=False,
        ),
        DrawArgs(
            metric="Count",
            title="Mean Oracle Calls per Algorithm",
            group_file=False,
            log=True,
        ),
        DrawArgs(
            metric="Time",
            title="Mean Execution Time per Algorithm",
            group_file=False,
            log=True,
        ),
    ]

    for arg in args:
        fig, ax = plt.subplots()
        results.draw_bar(
            ax=ax,
            metric=arg.metric,
            title=arg.title,
            log=arg.log,
            group_file=arg.group_file,
        )
        fig.tight_layout()

    plt.show()


def main() -> None:
    draw("examples/bugs/binutils/results.json")
    draw("examples/bugs/valgrind/results.json")


if __name__ == "__main__":
    main()
