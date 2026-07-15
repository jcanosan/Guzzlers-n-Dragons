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
    ]

    # Cooking science ingestion (vector store)
    print(f"\n{'=' * 60}")
    print("Running ingest_cooking_science.py...")
    print(f"{'=' * 60}")
    ingest_result = subprocess.run(
        [sys.executable, "scripts/ingest_cooking_science.py"],
        capture_output=False,
    )
    if ingest_result.returncode != 0:
        print("FAILED: ingest_cooking_science.py")
        sys.exit(1)
    print("SUCCESS: ingest_cooking_science.py")

    all_success = True
    for script in scripts:
        if not run_script(script):
            all_success = False
            break

    if all_success:
        print("\n✅ All seeds completed successfully!")
    else:
        print("\n❌ Some seeds failed!")
        sys.exit(1)
