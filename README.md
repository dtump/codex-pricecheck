# Codex Pricecheck

Estimate the API-equivalent cost of local OpenAI Codex CLI sessions.

Codex Pricecheck reads the JSONL logs already stored in `~/.codex/sessions`,
keeps all processing local, and prints token use and an estimated USD cost per
session. It supports a single session file or recursive directory scans, and
can account for sessions that switch models.

> Estimates use the current public API prices embedded in the script. They are
> not OpenAI invoices and do not include every possible tool or service-tier
> charge.

## Requirements

Python 3. No third-party dependencies.

## Usage

```bash
# One session
./codex_session_cost.py ~/.codex/sessions/2026/07/20/rollout-....jsonl

# One day (recursive)
./codex_session_cost.py ~/.codex/sessions/2026/07/20

# A whole year (recursive)
./codex_session_cost.py ~/.codex/sessions/2026
```

Without sorting, results are in chronological filename order. Add `--sort` to
sort by cost, highest first:

```bash
./codex_session_cost.py ~/.codex/sessions/2026 --sort
./codex_session_cost.py ~/.codex/sessions/2026 --sort output
./codex_session_cost.py ~/.codex/sessions/2026 --sort filename --ascending
```

Supported sort columns are `pricing`, `filename`, `input`, `cached`, `output`,
and `model`.

## License

GNU Affero General Public License v3.0 or later. See [LICENSE](LICENSE).
