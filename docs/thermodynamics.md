# Thermodynamics For AI Factories

If you want to understand why AI infrastructure looks the way it does, thermodynamics is not optional. It is one of the deepest constraints in the whole system.

## The Core Idea

Almost all electrical power consumed by a compute system ends up as heat.

That means:

- more compute means more power draw
- more power draw means more heat
- more heat means harder cooling, denser plumbing, and stricter facility limits

So when people talk about `TPS/W`, they are not only talking about efficiency. They are also talking about how much heat has to be removed per unit of model output.

## Why This Matters For NVIDIA Systems

A modern AI factory is constrained by more than:

- raw compute
- memory bandwidth
- interconnect bandwidth

It is also constrained by:

- rack power density
- coolant loop design
- airflow and liquid cooling limits
- facility power delivery
- how much heat can be rejected from the site

This is why roadmap slides increasingly talk about:

- liquid-cooled systems
- rack-scale architectures
- gigawatt buildouts

instead of only talking about faster chips.

## Useful Mental Metrics

### Tokens Per Second Per Watt

`TPS/W` asks:

- how much useful model output do I get
- for each watt I pay for and then have to cool

This is one of the most important big-picture metrics in the repo because it bridges:

- model serving
- chip efficiency
- cooling cost
- facility scaling

### Energy Per Token

This is the inverse framing.

Instead of asking output per watt, ask:

- how many joules are needed per generated token

Lower `energy per token` means the system is improving in a way that matters physically and economically.

### Power Density

Two systems can consume the same total megawatts and still have very different engineering difficulty.

Why:

- one may spread the load across many racks
- the other may pack more power into fewer racks

Higher power density usually means harder thermal engineering.

## Why NVLink And NVSwitch Matter Thermally Too

People often think of `NVLink` only as bandwidth.

But from a system viewpoint, better local communication can also reduce waste:

- fewer inefficient data movements
- less idle waiting across devices
- higher utilization of expensive hardware

That can improve effective output per watt at the system level, even if the link itself also consumes power.

## Why Liquid Cooling Shows Up

Once rack power density rises far enough, air cooling becomes a weaker answer.

That is why the roadmap keeps emphasizing liquid-cooled integrated systems. The thermal problem is no longer a side issue. It becomes part of the architecture itself.

## Big Picture

The AI factory problem is:

- compute
- memory
- communication
- power delivery
- heat removal

all at once.

So if you want to understand the `Blackwell -> Rubin -> Feynman` story properly, learn the thermal story along with the compute story.

## How This Connects To The Repo

Read these together:

- [docs/power-and-scale.md](power-and-scale.md)
- [docs/keynote-roadmap.md](keynote-roadmap.md)
- [forecast/capacity_model.py](../forecast/capacity_model.py)

The forecast model is simple, but the reason it focuses on `TPS/W` and gigawatt-equivalent buildout is fundamentally thermodynamic.
