# Power, TPS/W, And Factory Scale

This is the part that turns the repo from "GPU notes" into systems thinking.

## Why `TPS/W` Matters

At large scale, the useful question is not only "how fast is the chip?" It is:

- how many tokens per second can the system serve
- at what quality level
- at what utilization
- per watt

That is why `TPS/W` becomes a first-class systems metric. If you improve `tokens per second per watt`, you either:

- serve more output with the same power budget, or
- hold output constant and reduce cost and facility pressure

## Why Gigawatts Matter

At factory scale, power stops being a background variable and becomes a hard external constraint. Once deployments are measured in hundreds of megawatts or gigawatts, you cannot think only in terms of chip specs. You have to think in terms of:

- site power availability
- cooling and rack density
- networking and switch density
- utilization across the fleet
- how much token demand can actually be served by the installed base

## Public Anchors

As of **March 19, 2026**, this repo uses these public anchors:

- NVIDIA's `October 2025` investor deck says token generation was doubling every two months and places `Feynman` on the `2028` roadmap.
- The same deck says Alphabet processed `980 trillion` tokens in a month across its AI services, up from `480 trillion` in May.
- The same deck says OpenAI and NVIDIA plan a multi-year build-out of at least `10 gigawatts`, with the first `1 gigawatt` launching in `2026` on the `Vera Rubin` platform.
- NVIDIA's public materials position modern AI infrastructure as a co-designed stack spanning chips, systems, networking, and software.

This repo treats those items as public source anchors, then builds explicit scenario models on top of them.

## What The Forecast Model Does

The forecast model in `forecast/capacity_model.py` projects monthly token output under three scenario drivers:

- deployed `gigawatt-equivalent` capacity
- `TPS/W` improvement over time
- token demand growth

It computes:

- `demand_tokens_per_month`
- `capacity_tokens_per_month`
- `served_tokens_per_month`

Where:

- `capacity = baseline_tokens * power_multiplier * tps_per_watt_index`
- `served = min(demand, capacity)`

That last line matters. It encodes the idea that demand may keep growing, but factories can still be power-constrained.

## Important Caveat

The scenario model is educational. It is not claiming to know NVIDIA's actual private deployment plans or the exact future industry total. It is a transparent model for reasoning about scale, not a hidden-source prediction engine.

## Files To Look At

- [forecast/capacity_model.py](../forecast/capacity_model.py)
- [data/forecast_scenarios.csv](../data/forecast_scenarios.csv)
- [docs/assets/forecast_tokens.svg](assets/forecast_tokens.svg)
- [docs/assets/forecast_gw_equivalent.svg](assets/forecast_gw_equivalent.svg)
