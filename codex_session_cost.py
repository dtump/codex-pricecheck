#!/usr/bin/env python3
"""Estimate API-equivalent cost from Codex CLI session JSONL files.

The script reads only the session's metadata and token counters.  It does not
send data anywhere.  Prices are USD per one million tokens; update PRICES when
OpenAI changes the API rate card.
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path


# input, cached input, output — USD per 1M tokens (checked 2026-09-12).
# Sources: https://developers.openai.com/api/docs/models/gpt-6-astra and
# https://developers.openai.com/api/docs/models/compare.  These are current
# public API prices, not historical invoice prices.
PRICES = {
    "gpt-6-astra": (10.00, 1.00, 50.00),
    "gpt-5.6-sol": (4.00, 0.40, 20.00),
    "gpt-5.6-terra": (2.00, 0.20, 12.00),
    "gpt-5.6-luna": (0.20, 0.02, 1.20),
    "gpt-5.5": (5.00, 0.50, 30.00),
    "gpt-5.4": (2.50, 0.25, 15.00),
    "gpt-5.4-mini": (0.75, 0.075, 4.50),
    "gpt-5.3-codex": (1.75, 0.175, 14.00),
    "gpt-5.2-codex": (1.75, 0.175, 14.00),
    "gpt-5.2": (1.75, 0.175, 14.00),
    "gpt-5.1-codex-mini": (0.25, 0.025, 2.00),
    "gpt-5.1-codex": (1.25, 0.125, 10.00),
    "gpt-5.1": (1.25, 0.125, 10.00),
    "gpt-5-codex": (1.25, 0.125, 10.00),
    "gpt-5-mini": (0.25, 0.025, 2.00),
    "gpt-5": (1.25, 0.125, 10.00),
    "codex-mini-latest": (1.50, 0.375, 6.00),
    "gpt-4.1-mini": (0.40, 0.10, 1.60),
    "gpt-4.1-nano": (0.10, 0.025, 0.40),
    "gpt-4.1": (2.00, 0.50, 8.00),
}


def get_model(record):
    payload = record.get("payload", {})
    if record.get("type") == "turn_context":
        return payload.get("model")
    if record.get("type") == "event_msg" and payload.get("type") == "thread_settings_applied":
        return payload.get("thread_settings", {}).get("model")
    return None


def pricing_for(model):
    """Return prices for a model, including dated API snapshot names."""
    for known_model in sorted(PRICES, key=len, reverse=True):
        if model == known_model or model.startswith(f"{known_model}-"):
            return PRICES[known_model]
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        type=Path,
        help="A rollout-*.jsonl file, or a directory to scan recursively",
    )
    parser.add_argument(
        "--sort",
        nargs="?",
        choices=("pricing", "filename", "input", "cached", "output", "model"),
        const="pricing",
        default=None,
        help="Sort by a column; use without a column for pricing, highest first",
    )
    parser.add_argument(
        "--ascending",
        action="store_true",
        help="Sort the selected column low-to-high / A-to-Z",
    )
    args = parser.parse_args()

    if args.path.is_file():
        files = [args.path]
    elif args.path.is_dir():
        files = sorted(args.path.rglob("*.jsonl"))
    else:
        parser.error(f"not a file or directory: {args.path}")

    rows = []
    unknown_events = 0
    grand_tokens = defaultdict(int)
    grand_total = 0.0

    for path in files:
        model = None
        totals = defaultdict(lambda: defaultdict(int))

        with path.open() as session:
            for line in session:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                model = get_model(record) or model
                payload = record.get("payload", {})
                if record.get("type") != "event_msg" or payload.get("type") != "token_count":
                    continue

                # last_token_usage is the incremental usage for this completed call.
                # Some status-only token events have ``info: null``.
                usage = (payload.get("info") or {}).get("last_token_usage", {})
                if not usage:
                    continue
                if not model:
                    unknown_events += 1
                    continue
                # Codex's input_tokens includes cached_input_tokens.  Bill only
                # the remainder at the normal input rate; the cached portion has
                # its own lower rate.
                cached = usage.get("cached_input_tokens", 0)
                totals[model]["input"] += max(0, usage.get("input_tokens", 0) - cached)
                totals[model]["cached"] += cached
                totals[model]["output"] += usage.get("output_tokens", 0)

        for used_model, tokens in sorted(totals.items()):
            prices = pricing_for(used_model)
            cost = None if not prices else sum(
                tokens[k] * price / 1_000_000
                for k, price in zip(("input", "cached", "output"), prices)
            )
            rows.append((path.name, tokens["input"], tokens["cached"], tokens["output"], used_model, cost))
            for key in ("input", "cached", "output"):
                grand_tokens[key] += tokens[key]
            if cost is not None:
                grand_total += cost

    if args.sort:
        sort_columns = {"filename": 0, "input": 1, "cached": 2, "output": 3, "model": 4, "pricing": 5}
        column = sort_columns[args.sort]
        if args.sort == "pricing":
            # Keep models whose price is not configured at the bottom.
            rows.sort(
                key=lambda row: (row[5] is None, (row[5] or 0) if args.ascending else -(row[5] or 0))
            )
        else:
            rows.sort(key=lambda row: row[column], reverse=not args.ascending)

    headers = ("filename", "input", "cached", "output", "model", "pricing")
    display_rows = [
        (filename, f"{input_tokens:,}", f"{cached:,}", f"{output:,}", model, "unknown" if cost is None else f"${cost:.4f}")
        for filename, input_tokens, cached, output, model, cost in rows
    ]
    total_row = (
        "TOTAL",
        f"{grand_tokens['input']:,}",
        f"{grand_tokens['cached']:,}",
        f"{grand_tokens['output']:,}",
        "",
        f"${grand_total:.4f}",
    )
    widths = [len(header) for header in headers]
    # Include the total when sizing columns: monthly/yearly totals can be
    # wider than any individual session total.
    for row in [*display_rows, total_row]:
        widths = [max(width, len(value)) for width, value in zip(widths, row)]

    # The standard library has no table renderer.  Keep this dependency-free,
    # but right-align token counts and prices like a normal numeric table.
    numeric_columns = {1, 2, 3, 5}

    def print_row(row, *, header=False):
        cells = []
        for index, (value, width) in enumerate(zip(row, widths)):
            cells.append(value.rjust(width) if index in numeric_columns and not header else value.ljust(width))
        print("  ".join(cells))

    print_row(headers, header=True)
    print_row(tuple("-" * width for width in widths))
    for row in display_rows:
        print_row(row)

    print_row(tuple("-" * width for width in widths))
    print_row(total_row)

    if unknown_events:
        print(f"Warning: {unknown_events} token event(s) had no preceding model metadata.")


if __name__ == "__main__":
    main()
