from __future__ import annotations

import csv
from pathlib import Path
import sys
from typing import Dict, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from forecast.capacity_model import OBSERVED_METRICS, project_all_scenarios

DATA_DIR = ROOT / "data"
ASSETS_DIR = ROOT / "docs" / "assets"


def tokens_to_quadrillions(tokens: float) -> float:
    return tokens / 1e15


def write_observed_csv() -> Path:
    path = DATA_DIR / "observed_tokens.csv"
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["month", "label", "monthly_tokens", "monthly_tokens_q", "source_url"])
        for metric in OBSERVED_METRICS:
            writer.writerow(
                [
                    metric.observed_month.isoformat(),
                    metric.label,
                    int(metric.monthly_tokens),
                    f"{tokens_to_quadrillions(metric.monthly_tokens):.3f}",
                    metric.source_url,
                ]
            )
    return path


def write_forecast_csv() -> Path:
    path = DATA_DIR / "forecast_scenarios.csv"
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "month",
                "scenario",
                "power_gw_equivalent",
                "tps_per_watt_index",
                "demand_tokens",
                "capacity_tokens",
                "served_tokens",
                "served_tokens_q",
            ]
        )
        for point in project_all_scenarios():
            writer.writerow(
                [
                    point.month.isoformat(),
                    point.scenario,
                    f"{point.power_gw_equivalent:.3f}",
                    f"{point.tps_per_watt_index:.3f}",
                    int(point.demand_tokens),
                    int(point.capacity_tokens),
                    int(point.served_tokens),
                    f"{tokens_to_quadrillions(point.served_tokens):.3f}",
                ]
            )
    return path


def scale_point(
    x_index: int,
    x_count: int,
    y_value: float,
    y_max: float,
    width: int,
    height: int,
    left: int,
    top: int,
) -> Tuple[float, float]:
    x_span = width - left - 30
    y_span = height - top - 40
    x = left + (x_span * x_index / max(x_count - 1, 1))
    y = top + y_span - (y_span * y_value / max(y_max, 1e-9))
    return x, y


def line_path(
    values: Sequence[float],
    width: int,
    height: int,
    left: int,
    top: int,
    y_max: float,
) -> str:
    points = [
        scale_point(index, len(values), value, y_max, width, height, left, top)
        for index, value in enumerate(values)
    ]
    return " ".join(
        [f"M {points[0][0]:.1f} {points[0][1]:.1f}"]
        + [f"L {x:.1f} {y:.1f}" for x, y in points[1:]]
    )


def svg_template(
    title: str,
    x_labels: Sequence[str],
    series: Sequence[Tuple[str, Sequence[float], str]],
    y_label: str,
) -> str:
    width = 960
    height = 520
    left = 90
    top = 40
    y_max = max(max(values) for _, values, _ in series)
    y_ticks = 5
    grid_lines: List[str] = []
    label_lines: List[str] = []
    for tick in range(y_ticks + 1):
        value = y_max * tick / y_ticks
        _, y = scale_point(0, 2, value, y_max, width, height, left, top)
        grid_lines.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width - 30}" y2="{y:.1f}" stroke="#d7dde5" stroke-width="1" />'
        )
        label_lines.append(
            f'<text x="{left - 12}" y="{y + 4:.1f}" text-anchor="end" font-size="12" fill="#334155">{value:.1f}</text>'
        )
    x_tick_labels: List[str] = []
    chosen_indexes = sorted(set([0, len(x_labels) // 3, (2 * len(x_labels)) // 3, len(x_labels) - 1]))
    for index in chosen_indexes:
        x, y = scale_point(index, len(x_labels), 0, y_max, width, height, left, top)
        x_tick_labels.append(
            f'<text x="{x:.1f}" y="{y + 26:.1f}" text-anchor="middle" font-size="12" fill="#334155">{x_labels[index]}</text>'
        )
    legend_lines: List[str] = []
    for index, (label, _, color) in enumerate(series):
        y = 26 + index * 20
        legend_lines.append(
            f'<line x1="690" y1="{y}" x2="714" y2="{y}" stroke="{color}" stroke-width="3" />'
        )
        legend_lines.append(
            f'<text x="722" y="{y + 4}" font-size="12" fill="#0f172a">{label}</text>'
        )
    paths = [
        f'<path d="{line_path(values, width, height, left, top, y_max)}" fill="none" stroke="{color}" stroke-width="3" />'
        for _, values, color in series
    ]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#f8fafc" />
  <text x="{left}" y="26" font-size="22" font-weight="700" fill="#0f172a">{title}</text>
  <text x="24" y="{height / 2:.1f}" transform="rotate(-90 24 {height / 2:.1f})" font-size="13" fill="#334155">{y_label}</text>
  <line x1="{left}" y1="{height - 40}" x2="{width - 30}" y2="{height - 40}" stroke="#475569" stroke-width="1.5" />
  <line x1="{left}" y1="{top}" x2="{left}" y2="{height - 40}" stroke="#475569" stroke-width="1.5" />
  {' '.join(grid_lines)}
  {' '.join(label_lines)}
  {' '.join(paths)}
  {' '.join(x_tick_labels)}
  {' '.join(legend_lines)}
</svg>
"""


def grouped_series() -> Dict[str, List[dict]]:
    grouped: Dict[str, List[dict]] = {}
    forecast_csv = DATA_DIR / "forecast_scenarios.csv"
    with forecast_csv.open() as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            grouped.setdefault(row["scenario"], []).append(row)
    return grouped


def write_observed_svg() -> Path:
    path = ASSETS_DIR / "observed_tokens.svg"
    x_labels = [metric.observed_month.strftime("%Y-%m") for metric in OBSERVED_METRICS]
    values = [tokens_to_quadrillions(metric.monthly_tokens) for metric in OBSERVED_METRICS]
    path.write_text(
        svg_template(
            "Observed Monthly Token Anchors",
            x_labels,
            [("public token datapoints", values, "#0f766e")],
            "Quadrillion tokens per month",
        )
    )
    return path


def write_forecast_svgs() -> List[Path]:
    grouped = grouped_series()
    months = [row["month"] for row in next(iter(grouped.values()))]
    forecast_path = ASSETS_DIR / "forecast_tokens.svg"
    forecast_path.write_text(
        svg_template(
            "Projected Served Tokens Through 2028",
            months,
            [
                (
                    name,
                    [float(row["served_tokens_q"]) for row in rows],
                    color,
                )
                for name, color, rows in [
                    ("conservative", "#2563eb", grouped["conservative"]),
                    ("base", "#f59e0b", grouped["base"]),
                    ("factory_race", "#dc2626", grouped["factory_race"]),
                ]
            ],
            "Quadrillion tokens per month",
        )
    )
    power_path = ASSETS_DIR / "forecast_gw_equivalent.svg"
    power_path.write_text(
        svg_template(
            "Projected Buildout Constraint Through 2028",
            months,
            [
                (
                    name,
                    [float(row["power_gw_equivalent"]) for row in rows],
                    color,
                )
                for name, color, rows in [
                    ("conservative", "#2563eb", grouped["conservative"]),
                    ("base", "#f59e0b", grouped["base"]),
                    ("factory_race", "#dc2626", grouped["factory_race"]),
                ]
            ],
            "Gigawatt-equivalent buildout",
        )
    )
    return [forecast_path, power_path]


def main() -> int:
    DATA_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)
    write_observed_csv()
    write_forecast_csv()
    write_observed_svg()
    write_forecast_svgs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
