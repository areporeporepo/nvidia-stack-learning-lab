# Automation Notes

The repo is designed for future AI-assisted updates, including a possible NVIDIA NIM-backed summarizer.

## Secure Setup

Never put credentials in the repo. Use environment variables instead.

Suggested local variables:

```bash
export NVIDIA_API_KEY='...'
export NIM_BASE_URL='https://integrate.api.nvidia.com/v1'
export NIM_MODEL='your-model-name'
```

If you later automate updates in GitHub Actions, store secrets in the repository settings and read them at runtime.

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
