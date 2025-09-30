#!/usr/bin/env python3
"""
collect_drop.py - Verification of model weights directory structure for Oracle850B-MoE.

Validates that the checkpoint directory contains valid shard names and required files.
Returns sorted list of shards and total count.

Usage:
    python scripts/weights/collect_drop.py --ckpt_dir checkpoints/oracle850b
"""

import argparse
import os
import re
import sys
from pathlib import Path


def collect_and_verify_shards(ckpt_dir: str) -> tuple[list[Path], int]:
    """
    Scans directory and returns list of shards with verification.

    Args:
        ckpt_dir: Path to checkpoints directory.

    Returns:
        Tuple: (list of shards, total count).

    Raises:
        SystemExit: If structure is invalid.
    """
    ckpt_path = Path(ckpt_dir)

    # Check required files
    required_files = [
        "config.json",
        "generation_config.json",
        "model.safetensors.index.json",
    ]
    for file in required_files:
        if not (ckpt_path / file).exists():
            print(f"Error: Missing required file {file}")
            sys.exit(1)

    # Check tokenizer directory
    tokenizer_dir = ckpt_path / "tokenizer"
    if not tokenizer_dir.exists():
        print("Error: Missing tokenizer directory")
        sys.exit(1)

    # Find shard files (updated for 128 shards)
    shard_pattern = re.compile(r"^model-\d{5}-of-\d{5}\.safetensors$")
    shards = []
    for file_path in ckpt_path.glob("model-*-of-*.safetensors"):
        if shard_pattern.match(file_path.name):
            shards.append(file_path)
        else:
            print(f"Warning: Invalid shard name {file_path.name}")

    if not shards:
        print("Error: No shard files found")
        sys.exit(1)

    # Sort by shard number
    shards.sort(key=lambda x: int(x.name.split("-")[1]))

    total_shards = len(shards)
    print(f"Found {total_shards} shards:")
    for shard in shards:
        size_mb = shard.stat().st_size / (1024 * 1024)
        print(f"  {shard.name} ({size_mb".1f"} MB)")

    return shards, total_shards


def main():
    parser = argparse.ArgumentParser(description="Verify checkpoint directory structure")
    parser.add_argument(
        "--ckpt_dir",
        type=str,
        default="checkpoints/oracle850b",
        help="Path to checkpoints directory",
    )
    args = parser.parse_args()

    try:
        shards, total = collect_and_verify_shards(args.ckpt_dir)
        print(f"\nSuccess: Verification passed. Total shards: {total}")
        return 0
    except SystemExit as e:
        return e.code
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
