# Perf Results

Generated benchmark JSON artifacts for EP-010 M4 live in this directory.

Canonical command:

```sh
uv run pytest tests/perf --benchmark-only --benchmark-json=tests/perf/results/baseline.json
```

Notes:

- `baseline.json` is generated output, not hand-edited source.
- The current benchmark modules measure the callable surfaces that exist in this checkout.
- L1, L3, and L4 still benchmark placeholder or stub-level paths until the real layer implementations land.
