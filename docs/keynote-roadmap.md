# Reading The Roadmap Slide

This page explains the NVIDIA roadmap slide family that shows up in recent keynote and investor materials. The screenshot you shared is best read as a **systems roadmap**, not a simple GPU roadmap.

See the clean redraw here:

- [docs/assets/keynote-roadmap-clean.svg](assets/keynote-roadmap-clean.svg)

## What The Slide Is Actually Doing

It groups the roadmap into three platform eras:

- `Blackwell`
- `Rubin`
- `Feynman`

And it organizes each era across multiple stack layers:

- `Compute`
- `CPU`
- `Scale-Up`
- `Scale-Out`
- `System`

That is the main idea. NVIDIA is telling you that the platform advances as a coordinated stack, not as an isolated chip release.

## How To Read Each Row

### Compute

This row is about the main GPU generation and memory package direction.

In the simplified redraw:

- `Blackwell` is shown as `Blackwell` and `Blackwell Ultra`
- `Rubin` is shown as `Rubin` and `Rubin Ultra`
- `Feynman` is shown as roadmap-only with `next-gen HBM`

### CPU

This row reminds you that the host CPU is part of the platform story.

- `Grace CPU` is paired with the `Blackwell` era
- `Vera CPU` shows up as the host-side platform direction in later eras

### Scale-Up

This is the in-domain fabric layer inside a tightly coupled AI system.

This is where things like:

- `NVLink`
- `NVSwitch`
- `NVL72`

belong.

This row matters because it tells you how fast and how tightly groups of GPUs can communicate inside a node or rack-scale domain.

### Scale-Out

This is the networking layer outside the local GPU domain.

This is where things like:

- `Spectrum`
- `ConnectX`

belong.

This row matters because once the workload no longer fits in one tightly coupled fabric island, you are in the world of cluster networking and data center buildout.

### System

This row is the integrated machine or rack-scale package.

That is why system names such as:

- `Oberon NVL72`
- `Kyber NVL576`

show up separately from the chips and switches.

## What The Slide Is Trying To Convince You Of

The core message is:

- annual cadence
- full-stack co-design
- one architecture across chips, fabric, networking, and software
- scaling toward gigawatt AI factories

That is why this repo cares about `TPS/W`, power constraints, and system integration instead of only chip FLOPS.

## Important Caveat About Feynman

`Feynman` should be read as a **roadmap horizon**, not as a fully public detailed architecture disclosure.

So when we redraw the slide, we keep `Feynman` intentionally more abstract:

- future compute generation
- future memory packaging
- future scale-up switch generation
- future scale-out networking

but not a fake floorplan or fake benchmark table.

## Why We Redrew It

The keynote screenshot is useful, but not ideal for study:

- it is cluttered
- it contains stage context
- it is hard to read line by line

The clean redraw in this repo keeps the architecture meaning while stripping away the presentation noise.
