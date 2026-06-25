# -*- coding: utf-8 -*-
# ЛР №1, вариант 50
# Уравнение: sqrt(1-x) = 5*sin(x)
# Методы: бисекция и секущие

from __future__ import annotations

import math
import os

EPS = 0.01
SCAN_START = -10.0
SCAN_END = 1.0
SCAN_STEP = 0.05


def f(x: float) -> float:
    # функция из задания, корень только при x <= 1
    if x > 1.0:
        return float("nan")
    return math.sqrt(1.0 - x) - 5.0 * math.sin(x)


def localize_roots(
    func,
    start: float = SCAN_START,
    end: float = SCAN_END,
    step: float = SCAN_STEP,
) -> list[tuple[float, float]]:
    # ищем отрезки где функция меняет знак
    brackets: list[tuple[float, float]] = []
    x = start
    prev_x = x
    prev_y = func(prev_x)

    x += step
    while x <= end:
        y = func(x)
        if math.isnan(prev_y) or math.isnan(y):
            prev_x, prev_y = x, y
            x += step
            continue
        if prev_y == 0:
            brackets.append((prev_x, prev_x))
        elif y == 0:
            brackets.append((x, x))
        elif prev_y * y < 0:
            brackets.append((prev_x, x))
        prev_x, prev_y = x, y
        x += step

    return merge_brackets(brackets)


def merge_brackets(brackets: list[tuple[float, float]], gap: float = 0.2) -> list[tuple[float, float]]:
    # склеиваем близкие интервалы
    if not brackets:
        return []

    merged = [brackets[0]]
    for left, right in brackets[1:]:
        prev_left, prev_right = merged[-1]
        if left - prev_right <= gap:
            merged[-1] = (prev_left, right)
        else:
            merged.append((left, right))
    return merged


def bisection(func, left: float, right: float, eps: float = EPS) -> tuple[float, int]:
    # бисекция
    if left == right:
        return left, 0

    iterations = 0
    while right - left > eps:
        middle = (left + right) / 2
        if func(left) * func(middle) <= 0:
            right = middle
        else:
            left = middle
        iterations += 1
    return (left + right) / 2, iterations


def secant(func, x0: float, x1: float, eps: float = EPS) -> tuple[float, int]:
    # метод секущих
    iterations = 0
    while iterations < 100:
        f0, f1 = func(x0), func(x1)
        if abs(f1) < eps:
            return x1, iterations
        if abs(f1 - f0) < 1e-14:
            break
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        if abs(x2 - x1) < eps:
            return x2, iterations + 1
        x0, x1 = x1, x2
        iterations += 1
    return x1, iterations


def solve_all_roots() -> list[dict]:
    # считаем корни на каждом интервале двумя методами
    brackets = localize_roots(f)
    results = []

    for index, (left, right) in enumerate(brackets, start=1):
        root_b, it_b = bisection(f, left, right)
        x0 = left
        x1 = right if right != left else left + 0.1
        root_s, it_s = secant(f, x0, x1)
        results.append(
            {
                "index": index,
                "bracket": (left, right),
                "bisection": root_b,
                "bisection_iters": it_b,
                "secant": root_s,
                "secant_iters": it_s,
            }
        )
    return results


def format_output(results: list[dict]) -> str:
    # текст для консоли и отчёта
    lines = [
        "ЛР №1. Уравнение sqrt(1-x) = 5*sin(x)",
        "Точность: 0.01",
        "=" * 42,
        "",
        f"Найдено интервалов с корнями: {len(results)}",
        "",
    ]
    for item in results:
        left, right = item["bracket"]
        lines.append(f"Корень {item['index']}: интервал [{left:.2f}; {right:.2f}]")
        lines.append(f"  Бисекция:  x = {item['bisection']:.6f}, итераций {item['bisection_iters']}")
        lines.append(f"  Секущие:   x = {item['secant']:.6f}, итераций {item['secant_iters']}")
        lines.append(f"  f(x) бисекция: {f(item['bisection']):.2e}")
        lines.append("")
    return "\n".join(lines)


def save_plot(results: list[dict]) -> None:
    # график для отчёта
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Matplotlib не установлен.")
        return

    report_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Otchet")
    os.makedirs(report_dir, exist_ok=True)

    xs = np.linspace(SCAN_START, SCAN_END, 2000)
    ys = [f(x) for x in xs]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(xs, ys, label="f(x) = sqrt(1-x) - 5*sin(x)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.grid(True, linestyle="--", alpha=0.4)

    for item in results:
        ax.axvspan(item["bracket"][0], item["bracket"][1], color="yellow", alpha=0.2)
        ax.plot(item["bisection"], 0, "ro", label="корень (бисекция)")
        ax.plot(item["secant"], f(item["secant"]), "g^", label="корень (секущие)")

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys())
    ax.set_title("Отделение корней уравнения sqrt(1-x) = 5*sin(x)")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")

    path = os.path.join(report_dir, "lab1_plot.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"График сохранён: {path}")


def save_output_image(text: str, filename: str) -> None:
    # скриншот вывода
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    report_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Otchet")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis("off")
    ax.text(0.02, 0.98, text, va="top", ha="left", family="monospace", fontsize=9)
    path = os.path.join(report_dir, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Скриншот сохранён: {path}")


def main() -> None:
    results = solve_all_roots()
    if not results:
        print("Корни на заданном интервале не найдены.")
        return

    output = format_output(results)
    print(output)
    save_plot(results)
    save_output_image(output, "lab1_output.png")


if __name__ == "__main__":
    main()
