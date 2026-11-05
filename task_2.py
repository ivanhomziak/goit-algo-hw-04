"""Task 2: recursively draw the Koch snowflake using turtle graphics."""

import argparse
from math import sqrt
from typing import Protocol


class Pen(Protocol):
    def forward(self, distance: float) -> None: ...
    def left(self, angle: float) -> None: ...
    def right(self, angle: float) -> None: ...


def koch_segment(pen: Pen, length: float, depth: int) -> None:
    """Draw one Koch curve segment recursively."""
    if depth == 0:
        pen.forward(length)
        return

    segment_length = length / 3
    koch_segment(pen, segment_length, depth - 1)
    pen.left(60)
    koch_segment(pen, segment_length, depth - 1)
    pen.right(120)
    koch_segment(pen, segment_length, depth - 1)
    pen.left(60)
    koch_segment(pen, segment_length, depth - 1)


def draw_snowflake(pen: Pen, length: float, depth: int) -> None:
    """Draw three Koch segments forming a closed snowflake."""
    for _ in range(3):
        koch_segment(pen, length, depth)
        pen.right(120)


def main() -> None:
    parser = argparse.ArgumentParser(description="Сніжинка Коха з рекурсією.")
    parser.add_argument(
        "--depth", type=int, default=None,
        help="Рівень рекурсії від 0 до 6 (якщо не вказано — введення з клавіатури)",
    )
    parser.add_argument("--length", type=float, default=450, help="Довжина сторони (> 0)")
    args = parser.parse_args()

    try:
        depth = args.depth if args.depth is not None else int(
            input("Введіть рівень рекурсії (0–6): ")
        )
    except ValueError:
        parser.error("Рівень рекурсії має бути цілим числом.")

    if not 0 <= depth <= 6:
        parser.error("Рівень рекурсії має бути від 0 до 6.")
    if not 0 < args.length <= 900:
        parser.error("Довжина сторони має бути більшою за 0 і не більшою за 900.")

    import turtle  # A graphical desktop environment is required only when running.

    screen = turtle.Screen()
    screen.title(f"Сніжинка Коха — рівень {depth}")
    screen.setup(width=1050, height=900)
    screen.tracer(0, 0)

    pen = turtle.Turtle()
    pen.hideturtle()
    pen.speed(0)
    pen.pensize(2)
    pen.penup()
    # Center the original equilateral triangle around the origin.
    pen.goto(-args.length / 2, args.length * sqrt(3) / 6)
    pen.pendown()

    draw_snowflake(pen, args.length, depth)
    screen.update()
    screen.mainloop()


if __name__ == "__main__":
    main()
