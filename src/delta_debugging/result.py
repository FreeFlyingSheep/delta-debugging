"""Result for benchmark runs and collection of results."""

import logging
import json
import os
from dataclasses import dataclass
from typing import Any, Self

import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from tabulate import tabulate


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Result:
    """Result of a test case run."""

    file: str
    """File where the input is from."""
    algorithm: str
    """Name of the algorithm used."""
    cache: str
    """Name of the cache used."""
    input_size: int
    """Size of the input."""
    output_size: int
    """Size of the output."""
    count: int
    """Number of calls to the oracle function."""
    time: float
    """Time (in seconds) taken for the test case run."""

    @property
    def reduction_ratio(self) -> float:
        """Compute the reduction ratio.

        If the input size is 0, the reduction ratio is defined to be 1.0.

        Returns:
            The reduction ratio.

        """
        if self.input_size == 0:
            return 1.0
        else:
            return (self.input_size - self.output_size) / self.input_size

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        """Create a Result instance from a JSON dictionary.

        Args:
            data: JSON dictionary.

        Returns:
            A Result instance.

        """
        return cls(
            file=data["File"],
            algorithm=data["Algorithm"],
            cache=data["Cache"],
            input_size=data["Input Size"],
            output_size=data["Output Size"],
            count=data["Count"],
            time=data["Time"],
        )

    def to_json(self) -> dict[str, float | int | str]:
        """Convert the result to a JSON-serializable dictionary.

        Returns:
            A JSON-serializable dictionary representation of the result.

        """
        result: dict[str, float | int | str] = {
            "File": self.file,
            "Algorithm": self.algorithm,
            "Cache": self.cache,
            "Input Size": self.input_size,
            "Output Size": self.output_size,
            "Reduction Ratio": self.reduction_ratio,
            "Count": self.count,
            "Time": self.time,
        }
        return result


class ResultCollection:
    """Collection of Result instances."""

    _results: list[Result]
    """List of Result instances."""

    def __init__(self, results: list[Result] = []) -> None:
        """Initialize the ResultCollection.

        Args:
            results: List of Result instances.

        """
        self._results: list[Result] = results

    def __len__(self) -> int:
        """Get the number of results in the collection.

        Returns:
            The number of results.

        """
        return len(self._results)

    def add(self, result: Result) -> None:
        """Add a Result instance to the collection.

        Args:
            result: Result instance to add.

        """
        self._results.append(result)

    def load_results(self, file: str | os.PathLike | None) -> None:
        """Read results from file or the benchmark's file if specified.

        Args:
            file: File to read results from. If None, use the benchmark's file. If both are None, results will be empty.

        """
        self._results = []

        results: list[dict[str, float | int | str]] = []
        try:
            if file is not None:
                logger.debug(f"Reading results from file: {file}")
                with open(file, "r") as f:
                    results = json.load(f)
                for result in results:
                    self._results.append(Result.from_json(result))
            else:
                logger.warning(
                    "No file specified for reading results; results will be empty"
                )
                results = []
        except Exception:
            logger.exception("Error reading benchmark results from file")

    def store_results(self, file: str | os.PathLike) -> None:
        """Write results to file.

        Args:
            file: File to write results to.

        """
        with open(file, "w") as f:
            try:
                json.dump(self._results, f, indent=4)
            except Exception:
                logger.exception("Error writing benchmark results to file")

    def to_json(self) -> list[dict[str, float | int | str]]:
        """Convert the collection to a JSON-serializable list of dictionaries.

        Returns:
            A list of JSON-serializable dictionaries representing the results.

        """
        return [result.to_json() for result in self._results]

    def _remove_unique_column(
        self, column: str, results: list[dict[str, float | int | str]]
    ) -> None:
        """Remove a column from the results if it contains only a single unique value.

        Args:
            column: Column name to check and potentially remove.
            results: List of result dictionaries.

        """
        values: set[float | int | str] = set()
        for result in results:
            value: float | int | str = result[column]
            values.add(value)
            if len(values) > 1:
                break
        if len(values) <= 1:
            for result in results:
                del result[column]

    def to_string(self, remove_unique_columns: bool = True, **kwargs) -> str:
        """Get a string representation of the benchmark results.

        Args:
            remove_unique_columns: Whether to remove columns with a single unique value. Defaults to True.
            kwargs: Additional arguments to pass to tabulate. Defaults are:
                headers: "keys"
                floatfmt: ".2f"
                showindex: "always"

        """
        results: list[dict[str, float | int | str]] = self.to_json()

        if remove_unique_columns:
            self._remove_unique_column("File", results)
            self._remove_unique_column("Algorithm", results)
            self._remove_unique_column("Cache", results)

        if "headers" not in kwargs:
            kwargs["headers"] = "keys"
        if "floatfmt" not in kwargs:
            kwargs["floatfmt"] = ".2f"
        if "showindex" not in kwargs:
            kwargs["showindex"] = "always"

        return tabulate(results, **kwargs)

    def _filename(self, file: str) -> str:
        """Simplify file name for plotting.

        Args:
            file: File path.

        Returns:
            Simplified file name.

        """
        return os.path.basename(file)

    def _algorithm(self, algorithm: str) -> str:
        """Simplify algorithm name for plotting.

        Args:
            algorithm: Algorithm name.

        Returns:
            Simplified algorithm name.

        """
        if "HDD" in algorithm and "ddmin" in algorithm:
            return "HDD (ddmin)"
        elif "HDD" in algorithm and "ZipMin" in algorithm:
            return "HDD (ZipMin)"
        elif "HDD" in algorithm and "ProbDD" in algorithm:
            return "HDD (ProbDD)"
        else:
            return algorithm

    def _dataframe(self) -> pd.DataFrame:
        """Convert the collection to a Pandas DataFrame.

        Returns:
            A Pandas DataFrame representing the results.

        """
        df: pd.DataFrame = pd.DataFrame(self.to_json())
        df["File"] = df["File"].apply(self._filename)
        df["Algorithm"] = df["Algorithm"].apply(self._algorithm)
        return df

    def draw_bar(
        self,
        ax: Axes,
        metric: str,
        *,
        title: str | None = None,
        log: bool = False,
        group_file: bool = True,
        rotate_xticks: int = 45,
    ) -> None:
        """Draw a grouped bar chart of the specified metric by file and algorithm.

        Args:
            ax: Matplotlib Axes to draw on.
            metric: Metric to plot (e.g., "Count", "Time", "Reduction Ratio").
            title: Title of the plot.
            log: Whether to use a logarithmic scale for the y-axis.
            group_file: Whether to group by file.
            rotate_xticks: Angle to rotate x-tick labels.

        """
        df: pd.DataFrame = self._dataframe()
        if len(df) == 0:
            logger.warning("No results to plot")
            return

        if group_file:
            group: pd.Series = df.groupby(["File", "Algorithm"], as_index=False)[
                metric
            ].agg("mean")
            pivot: pd.DataFrame = group.pivot(
                index="File", columns="Algorithm", values=metric
            ).sort_index(axis=1)
            algorithms: list[str] = list(pivot.columns)
            x: np.ndarray = np.arange(len(pivot.index))
            width: float = 0.8 / len(algorithms)
            for i, algorithm in enumerate(algorithms):
                values: np.ndarray = pivot[algorithm].values.astype(float)
                ax.bar(
                    x + i * width - (len(algorithms) - 1) * width / 2,
                    values,
                    width,
                    label=algorithm,
                )
            ax.set_xlabel("File")
            ax.set_xticks(x)
            ax.set_xticklabels(
                [str(v) for v in pivot.index], rotation=rotate_xticks, ha="right"
            )
            ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), ncol=1)
        else:
            means: pd.Series = (
                df.groupby("Algorithm", as_index=True)[metric].mean().sort_index()
            )
            ax.bar(means.index, means.values.astype(float))
            ax.set_xlabel("Algorithm")
            ax.tick_params(axis="x", labelrotation=rotate_xticks)

        if log:
            ax.set_yscale("log")
        ax.set_ylabel(metric)
        if title:
            ax.set_title(title)
