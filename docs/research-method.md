# Research Method

This repo is meant to stay current through `2028`.

## Anchor Event

The anchor source is the official `GTC 2026` keynote by Jensen Huang:

- https://www.nvidia.com/gtc/keynote/4k/

That keynote is treated as a claim surface, not as a final truth source. The goal is to dissect it over time and compare:

- what was announced
- what was actually shipped
- what was delayed
- what changed in public messaging

## Update Rhythm

The intended update loop is:

1. Capture a new event or source.
2. Extract concrete claims.
3. Tag each claim as `shipping`, `roadmap`, `ecosystem`, `power`, `networking`, or `software`.
4. Update the notes and scenario inputs.
5. Regenerate the forecast assets.

## Event Set

The initial tracked events are:

- `GTC 2026`
- `Computex 2026`
- major NVIDIA product pages and investor materials
- major public partner disclosures that affect AI factory scale

## Automation Direction

This repo is designed to support future AI-assisted updates, but keys should never be committed.

Use:

- local environment variables for development
- GitHub Actions secrets for CI automation
- explicit source URLs in every generated note

Do not:

- paste API keys into repo files
- commit `.env` files
- let the summarizer overwrite source links or dates

## Prediction Discipline

Predictions in this repo should always identify:

- baseline date
- baseline public metric
- growth assumptions
- power assumptions
- efficiency assumptions
- what is inference versus directly sourced fact
