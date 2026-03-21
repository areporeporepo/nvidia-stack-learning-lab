# NVIDIA Stack Learning Lab

Educational notes, labs, and a small conceptual simulator for learning how NVIDIA AI systems fit together across `CUDA`, `NVLink`, `NVSwitch`, `NCCL`, `NVSHMEM`, `Blackwell`, `Rubin`, `Vera`, and the public `Feynman` roadmap.

This repo is for learning system architecture, not for reverse engineering unreleased hardware. Where NVIDIA has only published roadmap-level information, this repo says so directly.

As of **March 19, 2026**, the working thesis of this repo is that `2028` matters because NVIDIA publicly places `Feynman` on that roadmap horizon. The repo is designed to be updated over time as new keynote material, product pages, and event disclosures appear.

## What This Repo Covers

- How the modern NVIDIA stack fits together from chips to collectives
- The difference between compute, scale-up fabric, and scale-out networking
- Public roadmap context for `Blackwell`, `Rubin`, `Vera`, and `Feynman`
- Why `TPS/W` and gigawatt-scale factory constraints matter for token output
- Event-driven tracking anchored to `GTC 2026` and later public events
- Hands-on labs using public repos such as `cuda-samples` and `nccl-tests`
- A small Python fabric simulator for intuition about topology, bandwidth bottlenecks, and hop count
- A scenario model for monthly token output through the end of `2028`

## What This Repo Does Not Do

- Emulate `Blackwell`, `Rubin`, or `Feynman` at ISA or microarchitecture fidelity
- Reproduce exact private topologies or unpublished interconnect behavior
- Replace official NVIDIA documentation

## Learning Path

1. Read [docs/how-the-stack-fits.md](docs/how-the-stack-fits.md).
2. Read [docs/roadmap.md](docs/roadmap.md).
3. Read [docs/power-and-scale.md](docs/power-and-scale.md).
4. Read [docs/thermodynamics.md](docs/thermodynamics.md).
5. Read [docs/keynote-roadmap.md](docs/keynote-roadmap.md).
6. Read [docs/events-2026.md](docs/events-2026.md).
7. Read [docs/future-watchlist.md](docs/future-watchlist.md).
8. Read [docs/research-method.md](docs/research-method.md).
9. Run the simulator:

```bash
python3 -m sim.fabric_sim --preset dual_gpu_nvlink --size-gb 16
python3 -m sim.fabric_sim --preset nvswitch_box --source GPU0 --target GPU7 --size-gb 32
```

10. Generate the forecast assets:

```bash
python3 scripts/generate_projection_assets.py
```

11. Work through [labs/first-week.md](labs/first-week.md).
12. Use [labs/contribute.md](labs/contribute.md) to start contributing upstream.

## Repo Layout

- `docs/`: architecture notes and roadmap comparisons
- `events/`: event-specific notes, claims, and update checkpoints
- `automation/`: key-safe update workflow notes
- `.github/workflows/`: scheduled automation for future event tracking
- `labs/`: guided hands-on exercises and contribution ideas
- `forecast/`: power, efficiency, and token output scenario model
- `sim/`: conceptual topology simulator
- `tests/`: simulator tests

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip pytest ruff
ruff check .
pytest
python3 -m sim.fabric_sim --preset workstation_pcie
python3 scripts/generate_projection_assets.py
python3 scripts/update_future_events.py --dry-run
```

## Suggested Companion Repos

- `NVIDIA/cuda-samples`: https://github.com/NVIDIA/cuda-samples
- `NVIDIA/nccl-tests`: https://github.com/NVIDIA/nccl-tests
- `NVIDIA/nccl`: https://github.com/NVIDIA/nccl
- `NVIDIA/nvshmem`: https://github.com/NVIDIA/nvshmem

## Primary Sources

- NVIDIA Blackwell architecture: https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/
- NVIDIA HGX / Rubin overview: https://www.nvidia.com/en-us/data-center/hgx/
- NVIDIA Multi-Node NVLink Systems docs: https://docs.nvidia.com/multi-node-nvlink-systems/index.html
- NVIDIA NVLink overview: https://www.nvidia.com/en-us/data-center/nvlink/
- NVIDIA 2025 investor roadmap deck: https://investor.nvidia.com/files/doc_presentations/2025/10/NVIDIA-2025-NDR-Deck-1.pdf

## Design Principle

Use public facts for the roadmap, use current public software for hands-on learning, and use simple simulation only for intuition.

## Research Principle

Treat keynote claims as hypotheses to track over time. The repo should keep separating:

- what NVIDIA or other companies officially said
- what has shipped
- what is still roadmap
