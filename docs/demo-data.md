# Demo Data Guide

Use this to populate the app with a richer playable dataset (40–50+ mixed records).

## What it seeds

- ~45 demo wines by default (`Demo Wine ...`)
- multiple stores and offers per wine (pricing, discount, availability variety)
- mixed wine attributes to exercise filtering/scoring:
  - multiple wine types (`red`, `white`, `rose`, `sparkling`, `other`)
  - sweetness diversity (`dry`, `off-dry`, `sweet`)
  - some non-grape wines (`is_grape_wine=false`) for exclusion logic
- per-user tasting history for both `A` and `B`
- review aggregates/descriptors
- optional recommendation pipeline run to immediately fill Home lists

## Command

Seed default dataset and run pipeline:

- `python3 scripts/seed_demo_data.py`

Seed custom size:

- `python3 scripts/seed_demo_data.py --wines 50`

Seed without deleting existing demo rows:

- `python3 scripts/seed_demo_data.py --no-reset`

Seed without generating recommendations:

- `python3 scripts/seed_demo_data.py --no-run-pipeline`

## Notes

- Demo seeding is deterministic and designed for local play/testing.
- By default it resets demo-only records first, then repopulates cleanly.
- It does not commit generated data files into git.
