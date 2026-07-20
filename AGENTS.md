# AGENTS.md

## Project purpose

`codex_session_cost.py` is a dependency-free, local-only CLI for estimating
API-equivalent cost from Codex JSONL session logs.

## Development guidelines

- Keep the tool compatible with Python 3 and free of third-party dependencies.
- Do not upload, transmit, or persist session content.
- Treat embedded model prices as current estimates; cite and date changes to
  pricing data in code comments or release notes.
- Preserve support for both one JSONL file and recursive directory scans.
- Keep table output readable in a normal terminal.

## Verification

Run at least:

```bash
python3 -m py_compile codex_session_cost.py
./codex_session_cost.py --help
```
