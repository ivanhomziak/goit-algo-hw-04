"""Task 3: empirical comparison of insertion sort, merge sort, and Timsort."""

import argparse
import csv
import random
import timeit
from pathlib import Path
from typing import Callable


def insertion_sort(values: list[int]) -> list[int]:
    result = values.copy()
    for i in range(1, len(result)):
        current = result[i]
        j = i - 1
        while j >= 0 and result[j] > current:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = current
    return result


def merge_sort(values: list[int]) -> list[int]:
    if len(values) <= 1:
        return values.copy()

    middle = len(values) // 2
    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])
    merged: list[int] = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def timsort(values: list[int]) -> list[int]:
    return sorted(values)


def make_datasets(size: int) -> dict[str, list[int]]:
    """Create deterministic input distributions outside timed sections."""
    rng = random.Random(2026 + size)
    random_values = [rng.randint(-1_000_000, 1_000_000) for _ in range(size)]
    nearly_sorted = list(range(size))
    for _ in range(max(1, size // 100)):
        first, second = rng.sample(range(size), 2)
        nearly_sorted[first], nearly_sorted[second] = (
            nearly_sorted[second], nearly_sorted[first]
        )
    return {
        "random": random_values,
        "sorted": list(range(size)),
        "reversed": list(range(size, 0, -1)),
        "nearly_sorted": nearly_sorted,
        "few_unique": [rng.randint(0, 9) for _ in range(size)],
    }


def benchmark(sizes: list[int], repeats: int) -> list[dict[str, str | int | float]]:
    algorithms: dict[str, Callable[[list[int]], list[int]]] = {
        "insertion": insertion_sort,
        "merge": merge_sort,
        "timsort": timsort,
    }
    results: list[dict[str, str | int | float]] = []
    for size in sizes:
        for dataset, values in make_datasets(size).items():
            expected = sorted(values)
            for name, algorithm in algorithms.items():
                if algorithm(values) != expected:
                    raise AssertionError(f"Incorrect output: {name} on {dataset}/{size}")
                timer = timeit.Timer(lambda a=algorithm, v=values: a(v))
                seconds = min(timer.repeat(repeat=repeats, number=1))
                result = {
                    "dataset": dataset,
                    "size": size,
                    "algorithm": name,
                    "time_ms": round(seconds * 1000, 6),
                }
                results.append(result)
                print(f"{dataset:14} n={size:5} {name:10} {seconds * 1000:10.4f} ms")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Порівняння алгоритмів сортування.")
    parser.add_argument("--sizes", type=int, nargs="+", default=[100, 500, 1000, 2000, 5000])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, default=Path("results/benchmark_results.csv"))
    args = parser.parse_args()
    if any(size <= 0 for size in args.sizes) or args.repeats <= 0:
        parser.error("Розміри масивів і кількість повторів мають бути додатними.")

    results = benchmark(args.sizes, args.repeats)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["dataset", "size", "algorithm", "time_ms"])
        writer.writeheader()
        writer.writerows(results)
    print(f"\nРезультати збережені в {args.output}")


if __name__ == "__main__":
    main()
