# ЛР №2, задание 2.10
# Эквивалентное сопротивление мостовой цепи между точками A и B

from __future__ import annotations

import os

R = 120.0


def solve_resistance_210(base_r: float = R) -> dict[str, float]:
    # мостовая схема: верх R и R/2, низ R/2 и R, перемычка R
    r_top_left = base_r
    r_top_right = base_r / 2.0
    r_bottom_left = base_r / 2.0
    r_bottom_right = base_r
    r_bridge = base_r

    # узлы: A=0, B=1, T=2, D=3; задаём V_A=1, V_B=0
    conductance = [[0.0] * 4 for _ in range(4)]

    def add_resistor(node_a: int, node_b: int, resistance: float) -> None:
        g = 1.0 / resistance
        conductance[node_a][node_a] += g
        conductance[node_b][node_b] += g
        conductance[node_a][node_b] -= g
        conductance[node_b][node_a] -= g

    add_resistor(0, 2, r_top_left)
    add_resistor(2, 1, r_top_right)
    add_resistor(0, 3, r_bottom_left)
    add_resistor(3, 1, r_bottom_right)
    add_resistor(2, 3, r_bridge)

    # исключаем внутренние узлы T и D (индексы 2 и 3)
    g_tt = conductance[2][2]
    g_td = conductance[2][3]
    g_dd = conductance[3][3]
    b_top = -conductance[2][0] * 1.0 - conductance[2][1] * 0.0
    b_bottom = -conductance[3][0] * 1.0 - conductance[3][1] * 0.0

    det = g_tt * g_dd - g_td * g_td
    v_top = (b_top * g_dd - g_td * b_bottom) / det
    v_bottom = (g_tt * b_bottom - b_top * g_td) / det

    current_from_a = (1.0 - v_top) / r_top_left + (1.0 - v_bottom) / r_bottom_left
    equivalent = 1.0 / current_from_a

    path_top = r_top_left + r_top_right
    path_bottom = r_bottom_left + r_bottom_right
    without_bridge = 1.0 / (1.0 / path_top + 1.0 / path_bottom)

    return {
        "R_base": base_r,
        "R_AB": equivalent,
        "R_without_bridge": without_bridge,
        "V_top": v_top,
        "V_bottom": v_bottom,
    }


def format_output(values: dict[str, float]) -> str:
    lines = [
        "ЛР №2, задание 2.10. Сопротивление цепи",
        "=" * 40,
        f"R = {values['R_base']:.0f} Ом",
        "",
        "Расчет эквивалентного сопротивления R_AB:",
        f"  R_AB = {values['R_AB']:.4f} Ом",
        f"  R_AB (округл.) = {values['R_AB']:.2f} Ом",
        "",
        "Для сравнения (без перемычки):",
        f"  R (без перемычки) = {values['R_without_bridge']:.2f} Ом",
        "",
        "Перемычка уменьшает сопротивление между A и B.",
    ]
    return "\n".join(lines)


def save_output_image(text: str) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    report_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Otchet")
    os.makedirs(report_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.axis("off")
    ax.text(0.02, 0.98, text, va="top", ha="left", family="monospace", fontsize=10)
    path = os.path.join(report_dir, "lab2_resistance_output.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Скриншот сохранен: {path}")


def main() -> None:
    values = solve_resistance_210()
    output = format_output(values)
    print(output)
    save_output_image(output)


if __name__ == "__main__":
    main()
