#!/usr/bin/env python3
"""Run all database seeding scripts."""

import subprocess
import sys


def run_script(script_name: str) -> bool:
    print(f"\n{'=' * 60}")
    print(f"Running {script_name}...")
    print(f"{'=' * 60}")
    result = subprocess.run(
        [sys.executable, f"scripts/{script_name}"], capture_output=False
    )
    if result.returncode != 0:
        print(f"FAILED: {script_name}")
        return False
    print(f"SUCCESS: {script_name}")
    return True


if __name__ == "__main__":
    scripts = [
        "seed_fictional_ingredients.py",
        "seed_real_ingredients.py",
        "seed_recipe_patterns.py",
        "ingest_cooking_science.py",
    ]

    for script in scripts:
        if not run_script(script):
            print("\n❌ Some seeds failed!")
            sys.exit(1)

    print("\n✅ All seeds completed successfully!")
