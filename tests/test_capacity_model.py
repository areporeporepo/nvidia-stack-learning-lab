from forecast.capacity_model import (
    FORECAST_END,
    FORECAST_START,
    SCENARIOS,
    capacity_tokens_for_month,
    demand_tokens_for_month,
    power_gw_equivalent_for_month,
    project_all_scenarios,
    tps_per_watt_index_for_month,
)


def test_power_buildout_is_monotonic() -> None:
    scenario = SCENARIOS[1]
    start = power_gw_equivalent_for_month(scenario, FORECAST_START)
    end = power_gw_equivalent_for_month(scenario, FORECAST_END)
    assert end > start


def test_tps_per_watt_improves_over_time() -> None:
    scenario = SCENARIOS[1]
    start = tps_per_watt_index_for_month(scenario, FORECAST_START)
    end = tps_per_watt_index_for_month(scenario, FORECAST_END)
    assert end > start


def test_capacity_and_demand_are_positive() -> None:
    scenario = SCENARIOS[0]
    capacity = capacity_tokens_for_month(scenario, FORECAST_START)
    demand = demand_tokens_for_month(scenario, FORECAST_START)
    assert capacity > 0
    assert demand > 0


def test_served_tokens_do_not_exceed_limits() -> None:
    for point in project_all_scenarios():
        assert point.served_tokens <= point.capacity_tokens
        assert point.served_tokens <= point.demand_tokens
