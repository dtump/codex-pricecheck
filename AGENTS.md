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

## Pricing sources

Use OpenAI's official API model pages as the source of current token prices:

- Model catalogue: <https://developers.openai.com/api/docs/models>
- GPT-5.6 Sol, Terra, and Luna comparison: <https://developers.openai.com/api/docs/models/compare>
- GPT-5.5: <https://developers.openai.com/api/docs/models/gpt-5.5>
- GPT-5.4: <https://developers.openai.com/api/docs/models/gpt-5.4>
- GPT-5.4 mini: <https://developers.openai.com/api/docs/models/gpt-5.4-mini>
- GPT-5.3 Codex: <https://developers.openai.com/api/docs/models/gpt-5.3-codex>
- GPT-5.2: <https://developers.openai.com/api/docs/models/gpt-5.2>
- GPT-5.1 Codex: <https://developers.openai.com/api/docs/models/gpt-5.1-codex>
- GPT-5.1 Codex mini: <https://developers.openai.com/api/docs/models/gpt-5.1-codex-mini>
- Codex mini: <https://developers.openai.com/api/docs/models/codex-mini-latest>
- GPT-4.1 family: <https://developers.openai.com/api/docs/models/gpt-4.1>

Check the relevant source before changing `PRICES`, record the check date in
the code comment, and do not present estimates as historical invoice totals.

## Verification

Run at least:

```bash
python3 -m py_compile codex_session_cost.py
./codex_session_cost.py --help
```
