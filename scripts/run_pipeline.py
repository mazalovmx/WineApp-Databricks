from __future__ import annotations

import argparse

from app.db import SessionLocal
from app.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Guadalajara Wine Finder batch pipeline.")
    parser.add_argument("--mode", choices=["daily", "weekly", "manual"], default="daily")
    args = parser.parse_args()

    with SessionLocal() as session:
        result = run_pipeline(session, mode=args.mode)
    print(f"run_id={result.run_id} status={result.status} summary={result.summary_path}")


if __name__ == "__main__":
    main()
