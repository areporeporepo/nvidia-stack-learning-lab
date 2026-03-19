# Automation Notes

The repo is designed for future AI-assisted updates using NVIDIA NIM, with the default model set to `nvidia/nemotron-3-super-120b-a12b`.

## Secure Setup

Never put credentials in the repo. Use environment variables instead.

Suggested local variables:

```bash
export NVIDIA_API_KEY='...'
export NIM_BASE_URL='https://integrate.api.nvidia.com/v1'
export NIM_MODEL='nvidia/nemotron-3-super-120b-a12b'
```

If you later automate updates in GitHub Actions, store secrets in the repository settings and read them at runtime.

## Local Run

```bash
python3 scripts/update_future_events.py --dry-run
python3 scripts/update_future_events.py
```

Dry run verifies page fetches and file generation without calling NIM. A live run requires `NVIDIA_API_KEY`.

## GitHub Actions

The repo includes `.github/workflows/update-future-events.yml`.

Set these repository secrets:

- `NVIDIA_API_KEY`
- `NIM_BASE_URL` optional, defaults to `https://integrate.api.nvidia.com/v1`
- `NIM_MODEL` optional, defaults to `nvidia/nemotron-3-super-120b-a12b`

The workflow runs weekly and can also be triggered manually. It opens a PR instead of pushing directly to `main`.

## Outputs

Each run writes:

- dated notes under `events/*/updates/`
- a generated summary page at `docs/future-events-generated.md`
- machine-readable snapshot data at `data/future_event_snapshot.json`

## Safe Responsibilities For The Updater

- pull fresh public source URLs
- summarize new claims
- append dated notes
- regenerate charts
- open a PR with explicit source links

## Unsafe Responsibilities

- invent missing facts
- rewrite existing sourced claims without traceability
- store secrets in files or logs
