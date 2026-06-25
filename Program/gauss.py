# ЛР №2, вариант 50
# Решение СЛАУ методом Гаусса

from __future__ import annotations

import math
import os
import sys

EPS = 1e-10
MAX_SYSTEM_SIZE = 100


class LinearSystemError(Exception):
    # общая ошибка при решении
    pass


class InconsistentSystemError(LinearSystemError):
    # решений нет
    pass


class InfiniteSolutionsError(LinearSystemError):
    # решений бесконечно много
    pass


def read_positive_int(prompt: str, max_value: int = MAX_SYSTEM_SIZE) -> int:
    # проверка на ввод корректного числа
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("Ввод не может быть пустым.")
            continue
        try:
            value = int(raw)
        except ValueError:
            print("Введите целое число.")
            continue
        if value <= 0:
            print("Число должно быть положительным.")
            continue
        if value > max_value:
            print(f"Слишком большой размер системы. Максимум: {max_value}.")
            continue
        return value


def parse_number_list(raw: str) -> list[float]:
    # перевод строки в числа
    return list(map(float, raw.replace(",", ".").split()))


def read_floats(prompt: str, count: int) -> list[float]:
    # читаем ровно count чисел из одной строки
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("Ввод не может быть пустым.")
            continue
        try:
            values = parse_number_list(raw)
        except ValueError:
            print("Введите числа через пробел.")
            continue
        if len(values) != count:
            print(f"Нужно ввести ровно {count} чисел, получено {len(values)}.")
            continue
        return values


def read_system_by_matrix() -> tuple[list[list[float]], list[float]]:
    # ввод матрицы А построчно потом матрица В
    n = read_positive_int("Введите число уравнений (и неизвестных): ")

    print(f"\nВведите коэффициенты матрицы {n}x{n} (по одной строке):")
    matrix: list[list[float]] = []
    for i in range(n):
        row = read_floats(f"  Строка {i + 1}: ", n)
        matrix.append(row)

    print("\nВведите столбец свободных членов:")
    vector = read_floats("  b: ", n)

    validate_system(matrix, vector)
    return matrix, vector


def read_system_by_equations() -> tuple[list[list[float]], list[float]]:
    # ввод каждого уравнения одной строкой
    n = read_positive_int("Введите число уравнений (и неизвестных): ")

    print(
        f"\nВведите {n} уравнений."
        f"\nФормат строки: a1 a2 ... a{n} b"
        f"\nПример для n=3: 2 1 -1 8  означает  2*x1 + 1*x2 + (-1)*x3 = 8"
    )

    matrix: list[list[float]] = []
    vector: list[float] = []

    for i in range(n):
        while True:
            raw = input(f"  Уравнение {i + 1}: ").strip()
            if not raw:
                print("  Ввод не может быть пустым.")
                continue
            try:
                values = parse_number_list(raw)
            except ValueError:
                print("  Введите числа через пробел.")
                continue
            if len(values) != n + 1:
                print(f"  Нужно ввести {n} коэффициентов и 1 свободный член ({n + 1} чисел).")
                continue
            matrix.append(values[:-1])
            vector.append(values[-1])
            break

    validate_system(matrix, vector)
    return matrix, vector


def print_entered_system(matrix: list[list[float]], vector: list[float]) -> None:
    # вывод введенной пользователем системы
    n = len(vector)
    print("\nВведенная система:")
    for i in range(n):
        terms = " + ".join(f"({matrix[i][j]:g})*x{j + 1}" for j in range(n))
        print(f"  {terms} = {vector[i]:g}")

    print("\nРасширенная матрица [A|b]:")
    for row in copy_augmented(matrix, vector):
        coeffs = "  ".join(f"{value:10.4f}" for value in row[:-1])
        print(f"  | {coeffs} | {row[-1]:10.4f} |")


def confirm_input() -> bool:
    # подтверждение ввода
    while True:
        answer = input("\nРешить эту систему? (д/н): ").strip().lower()
        if answer in {"д", "y", "yes", "да", "1"}:
            return True
        if answer in {"н", "n", "no", "нет", "0"}:
            return False
        print("Введите «д» (да) или «н» (нет).")


def choose_input_method() -> str:
    # выбор способа ввода 
    while True:
        print("\nСпособ ввода данных:")
        print("  1 - по уравнениям (рекомендуется)")
        print("  2 - матрица A и столбец b отдельно")
        choice = input("Выберите способ: ").strip()
        if choice in {"1", "2"}:
            return choice
        print("Неверный выбор. Введите 1 или 2.")


def read_system() -> tuple[list[list[float]], list[float]]:
    # выбор способа ввода 
    if choose_input_method() == "1":
        return read_system_by_equations()
    return read_system_by_matrix()


def validate_system(matrix: list[list[float]], vector: list[float]) -> None:
    # проверяем что размеры совпадают и нет мусора в данных
    if not matrix:
        raise ValueError("Матрица коэффициентов не может быть пустой.")

    n = len(matrix)
    if n > MAX_SYSTEM_SIZE:
        raise ValueError(f"Размер системы превышает допустимый максимум ({MAX_SYSTEM_SIZE}).")

    if not vector:
        raise ValueError("Столбец свободных членов не может быть пустым.")

    if len(vector) != n:
        raise ValueError(
            f"Размер вектора b ({len(vector)}) не совпадает с числом уравнений ({n})."
        )

    for row_index, row in enumerate(matrix, start=1):
        if len(row) != n:
            raise ValueError(
                f"Строка {row_index} содержит {len(row)} коэффициентов, ожидается {n}."
            )
        for col_index, value in enumerate(row, start=1):
            if not isinstance(value, (int, float)):
                raise ValueError(f"Элемент ({row_index}, {col_index}) не является числом.")
            if math.isnan(value) or math.isinf(value):
                raise ValueError(f"Недопустимое значение в позиции ({row_index}, {col_index}).")

    for index, value in enumerate(vector, start=1):
        if not isinstance(value, (int, float)):
            raise ValueError(f"Свободный член b[{index}] не является числом.")
        if math.isnan(value) or math.isinf(value):
            raise ValueError(f"Недопустимое значение в b[{index}].")


def copy_augmented(matrix: list[list[float]], vector: list[float]) -> list[list[float]]:
    # введенные матрицы А и В соединяются в одну 
    return [row[:] + [vector[i]] for i, row in enumerate(matrix)]


def find_pivot(augmented: list[list[float]], column: int, start_row: int = 0) -> int | None:
    # ищем в столбце самый большой по модулю элемент
    best_row = None
    best_value = 0.0
    for row in range(start_row, len(augmented)):
        value = abs(augmented[row][column])
        if value > best_value:
            best_value = value
            best_row = row
    return best_row if best_value > EPS else None


def gauss_solve(matrix: list[list[float]], vector: list[float]) -> tuple[list[float], list[list[float]]]:
    # метод Гаусса
    validate_system(matrix, vector)

    n = len(vector)
    augmented = copy_augmented(matrix, vector)
    steps = [copy_augmented(matrix, vector)]

    rank = 0
    for column in range(n):
        pivot_row = find_pivot(augmented, column, rank)
        if pivot_row is None:
            continue

        if pivot_row != rank:
            augmented[rank], augmented[pivot_row] = augmented[pivot_row], augmented[rank]

        pivot = augmented[rank][column]
        for row in range(rank + 1, n):
            factor = augmented[row][column] / pivot
            for col in range(column, n + 1):
                augmented[row][col] -= factor * augmented[rank][col]

        rank += 1
        steps.append([row[:] for row in augmented])

    for row in range(rank, n):
        coeffs_zero = all(abs(augmented[row][col]) < EPS for col in range(n))
        if coeffs_zero and abs(augmented[row][n]) > EPS:
            raise InconsistentSystemError(
                "Система несовместна: получено уравнение вида 0 = c, где c != 0."
            )

    if rank < n:
        raise InfiniteSolutionsError(
            "Система имеет бесконечно много решений (ранг матрицы меньше числа неизвестных)."
        )

    solution = [0.0] * n
    for row in range(n - 1, -1, -1):
        value = augmented[row][n]
        for col in range(row + 1, n):
            value -= augmented[row][col] * solution[col]
        pivot = augmented[row][row]
        if abs(pivot) < EPS:
            raise InfiniteSolutionsError(
                "Система имеет бесконечно много решений (вырожденная матрица)."
            )
        solution[row] = value / pivot

    return solution, steps


def verify_solution(matrix: list[list[float]], vector: list[float], solution: list[float]) -> list[float]:
    # подставляем ответ обратно и смотрим насколько сходится (Ax - b)
    residuals = []
    for i, row in enumerate(matrix):
        calculated = sum(row[j] * solution[j] for j in range(len(solution)))
        residuals.append(calculated - vector[i])
    return residuals


def demo_system() -> tuple[list[list[float]], list[float]]:
    # матрица варианта 50
    matrix = [
        [0.78, -0.02, -0.12],
        [0.02, -0.86, 0.04],
        [0.12, 0.44, -0.72],
    ]
    vector = [-0.56, 0.77, 1.01]
    return matrix, vector


def save_report_images(
    matrix: list[list[float]],
    vector: list[float],
    solution: list[float],
    residuals: list[float],
    output_text: str,
) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib не установлен. Графики для отчета не созданы.")
        return

    report_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Otchet")
    os.makedirs(report_dir, exist_ok=True)

    labels = [f"x{i + 1}" for i in range(len(solution))]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].bar(labels, solution, color="#4C72B0")
    axes[0].set_title("Найденное решение СЛАУ")
    axes[0].set_ylabel("Значение")
    axes[0].grid(axis="y", linestyle="--", alpha=0.4)

    axes[1].bar(labels, residuals, color="#DD8452")
    axes[1].set_title("Невязки Ax - b")
    axes[1].set_ylabel("Ошибка")
    axes[1].grid(axis="y", linestyle="--", alpha=0.4)

    fig.tight_layout()
    plot_path = os.path.join(report_dir, "gauss_solution.png")
    fig.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis("off")
    ax.text(
        0.02,
        0.98,
        output_text,
        va="top",
        ha="left",
        family="monospace",
        fontsize=10,
    )
    screenshot_path = os.path.join(report_dir, "gauss_output.png")
    fig.savefig(screenshot_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"График сохранен: {plot_path}")
    print(f"Скриншот вывода сохранен: {screenshot_path}")


def format_output(
    matrix: list[list[float]],
    vector: list[float],
    solution: list[float],
    residuals: list[float],
    steps: list[list[list[float]]],
) -> str:
    # текст с шагами Гаусса и итоговым ответом
    lines: list[str] = []
    lines.append("Решение СЛАУ методом Гаусса (вариант 50)")
    lines.append("=" * 40)
    lines.append("")
    lines.append("Исходная расширенная матрица [A|b]:")
    for row in copy_augmented(matrix, vector):
        coeffs = "  ".join(f"{value:8.3f}" for value in row[:-1])
        lines.append(f"| {coeffs} | {row[-1]:8.3f} |")
    lines.append("")

    for index, step in enumerate(steps[1:], start=1):
        lines.append(f"Шаг {index} прямого хода:")
        for row in step:
            coeffs = "  ".join(f"{value:8.3f}" for value in row[:-1])
            lines.append(f"| {coeffs} | {row[-1]:8.3f} |")
        lines.append("")

    lines.append("Найденное решение:")
    for i, value in enumerate(solution, start=1):
        lines.append(f"x{i} = {value:.6f}")

    lines.append("")
    lines.append("Проверка (Ax - b):")
    for i, value in enumerate(residuals, start=1):
        lines.append(f"Уравнение {i}: {value:.2e}")

    return "\n".join(lines)


def solve_and_print(matrix: list[list[float]], vector: list[float]) -> bool:
    try:
        solution, steps = gauss_solve(matrix, vector)
    except LinearSystemError as error:
        print(f"Ошибка решения: {error}")
        return False

    residuals = verify_solution(matrix, vector, solution)
    output_text = format_output(matrix, vector, solution, residuals, steps)
    print(output_text)
    save_report_images(matrix, vector, solution, residuals, output_text)

    return True


def ask_retry() -> bool:
    answer = input("Повторить ввод? (д/н): ").strip().lower()
    return answer in {"д", "y", "yes", "да", "1"}


def run_demo() -> None:
    matrix, vector = demo_system()
    solve_and_print(matrix, vector)


def run_interactive() -> None:
    print("\n=== Режим пользовательского ввода ===")

    while True:
        try:
            matrix, vector = read_system()
        except ValueError as error:
            print(f"Ошибка ввода: {error}")
            if not ask_retry():
                return
            continue

        print_entered_system(matrix, vector)
        if not confirm_input():
            if not ask_retry():
                return
            continue

        if solve_and_print(matrix, vector):
            return

        if not ask_retry():
            return


def read_menu_choice() -> str:
    # главное меню программы
    while True:
        print("\n=== Решение СЛАУ методом Гаусса ===")
        print("1 - ввести систему вручную (пользовательский ввод)")
        print("2 - демонстрационный пример")
        print("0 - выход")
        choice = input("Выберите режим: ").strip()
        if choice in {"0", "1", "2"}:
            return choice
        print("Неверный выбор. Введите 0, 1 или 2.")


def main() -> None:
    if len(sys.argv) > 1:
        flag = sys.argv[1].lower()
        if flag in {"--demo", "-d"}:
            run_demo()
            return
        if flag in {"--input", "-i", "--interactive"}:
            run_interactive()
            return

    choice = read_menu_choice()
    if choice == "0":
        return
    if choice == "1":
        run_interactive()
    elif choice == "2":
        run_demo()


if __name__ == "__main__":
    main()
