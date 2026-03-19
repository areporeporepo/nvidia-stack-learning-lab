from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, List


@dataclass(frozen=True)
class ObservedMetric:
    observed_month: date
    label: str
    monthly_tokens: float
    source_url: str


@dataclass(frozen=True)
class Scenario:
    name: str
    power_start_gw_equivalent: float
    power_end_gw_equivalent: float
    tps_per_watt_gain_per_year: float
    demand_growth_per_month: float


@dataclass(frozen=True)
class ProjectionPoint:
    month: date
    scenario: str
    power_gw_equivalent: float
    tps_per_watt_index: float
    demand_tokens: float
    capacity_tokens: float
    served_tokens: float


BASELINE_MONTH = date(2025, 10, 1)
FORECAST_START = date(2026, 3, 1)
FORECAST_END = date(2028, 12, 1)
BASELINE_MONTHLY_TOKENS = 1.3e15

OBSERVED_METRICS = [
    ObservedMetric(
        observed_month=date(2025, 5, 1),
        label="Alphabet AI services",
        monthly_tokens=4.8e14,
        source_url="https://blog.google/innovation-and-ai/technology/ai/io-2025-keynote/",
    ),
    ObservedMetric(
        observed_month=date(2025, 7, 1),
        label="Alphabet AI services",
        monthly_tokens=9.8e14,
        source_url="https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q2-2025/",
    ),
    ObservedMetric(
        observed_month=date(2025, 10, 1),
        label="Scenario calibration anchor",
        monthly_tokens=1.3e15,
        source_url="https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q3-2025/",
    ),
]

SCENARIOS = [
    Scenario(
        name="conservative",
        power_start_gw_equivalent=1.2,
        power_end_gw_equivalent=3.5,
        tps_per_watt_gain_per_year=1.35,
        demand_growth_per_month=1.07,
    ),
    Scenario(
        name="base",
        power_start_gw_equivalent=1.5,
        power_end_gw_equivalent=6.0,
        tps_per_watt_gain_per_year=1.70,
        demand_growth_per_month=1.10,
    ),
    Scenario(
        name="factory_race",
        power_start_gw_equivalent=1.8,
        power_end_gw_equivalent=10.0,
        tps_per_watt_gain_per_year=2.00,
        demand_growth_per_month=1.13,
    ),
]


def months_between(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + (end.month - start.month)


def month_sequence(start: date, end: date) -> List[date]:
    months: List[date] = []
    current = start
    while current <= end:
        months.append(current)
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return months


def power_gw_equivalent_for_month(scenario: Scenario, month: date) -> float:
    total_months = months_between(FORECAST_START, FORECAST_END)
    elapsed = months_between(FORECAST_START, month)
    if total_months == 0:
        return scenario.power_end_gw_equivalent
    ratio = elapsed / total_months
    return scenario.power_start_gw_equivalent + (
        scenario.power_end_gw_equivalent - scenario.power_start_gw_equivalent
    ) * ratio


def tps_per_watt_index_for_month(scenario: Scenario, month: date) -> float:
    elapsed_months = months_between(BASELINE_MONTH, month)
    return scenario.tps_per_watt_gain_per_year ** (elapsed_months / 12)


def demand_tokens_for_month(scenario: Scenario, month: date) -> float:
    elapsed_months = months_between(BASELINE_MONTH, month)
    return BASELINE_MONTHLY_TOKENS * (scenario.demand_growth_per_month ** elapsed_months)


def capacity_tokens_for_month(scenario: Scenario, month: date) -> float:
    power = power_gw_equivalent_for_month(scenario, month)
    efficiency = tps_per_watt_index_for_month(scenario, month)
    return BASELINE_MONTHLY_TOKENS * power * efficiency


def project_scenario(scenario: Scenario) -> List[ProjectionPoint]:
    points: List[ProjectionPoint] = []
    for month in month_sequence(FORECAST_START, FORECAST_END):
        demand = demand_tokens_for_month(scenario, month)
        capacity = capacity_tokens_for_month(scenario, month)
        points.append(
            ProjectionPoint(
                month=month,
                scenario=scenario.name,
                power_gw_equivalent=power_gw_equivalent_for_month(scenario, month),
                tps_per_watt_index=tps_per_watt_index_for_month(scenario, month),
                demand_tokens=demand,
                capacity_tokens=capacity,
                served_tokens=min(demand, capacity),
            )
        )
    return points


def project_all_scenarios(
    scenarios: Iterable[Scenario] = SCENARIOS,
) -> List[ProjectionPoint]:
    points: List[ProjectionPoint] = []
    for scenario in scenarios:
        points.extend(project_scenario(scenario))
    return points
