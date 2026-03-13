from __future__ import annotations

import argparse

from app.db import SessionLocal
from app.demo_data import seed_demo_data


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo records for Guadalajara Wine Finder.")
    parser.add_argument("--wines", type=int, default=45, help="Number of demo wines to create (default: 45).")
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Do not remove existing demo records before insert/update.",
    )
    parser.add_argument(
        "--no-run-pipeline",
        action="store_true",
        help="Do not trigger recommendation pipeline after seeding.",
    )
    args = parser.parse_args()

    with SessionLocal() as session:
        summary = seed_demo_data(
            session,
            total_wines=args.wines,
            reset=not args.no_reset,
            run_pipeline_after_seed=not args.no_run_pipeline,
        )

    print(
        "seeded "
        f"demo_wines={summary.demo_wines} "
        f"demo_offers={summary.demo_offers} "
        f"ratings_a={summary.ratings_a} "
        f"ratings_b={summary.ratings_b} "
        f"run_id={summary.run_id or 'none'}"
    )


if __name__ == "__main__":
    main()
