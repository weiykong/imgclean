"""Parallel processing helpers."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TypeVar

from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

T = TypeVar("T")
R = TypeVar("R")


def parallel_map(
    fn: Callable[[T], R],
    items: Iterable[T],
    max_workers: int | None = None,
    description: str = "Processing",
    show_progress: bool = True,
) -> list[R]:
    """
    Apply ``fn`` to each item using a thread pool.
    Returns results in the same order as ``items``.
    """
    items_list = list(items)
    if not items_list:
        return []

    results: list[R | None] = [None] * len(items_list)

    progress_ctx = (
        Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
        )
        if show_progress
        else _NullProgress()
    )

    with progress_ctx as progress:  # type: ignore[union-attr]
        task_id = progress.add_task(description, total=len(items_list))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {
                executor.submit(fn, item): idx for idx, item in enumerate(items_list)
            }
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                results[idx] = future.result()
                progress.advance(task_id)

    return results  # type: ignore[return-value]


class _NullProgress:
    """No-op context manager when progress display is disabled."""

    def __enter__(self) -> "_NullProgress":
        return self

    def __exit__(self, *_: object) -> None:
        pass

    def add_task(self, *_: object, **__: object) -> int:
        return 0

    def advance(self, *_: object) -> None:
        pass
