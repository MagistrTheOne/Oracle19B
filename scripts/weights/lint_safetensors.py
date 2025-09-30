#!/usr/bin/env python3
"""
lint_safetensors.py - Fast linting of safetensors files for Oracle850B-MoE.

Reads header of each shard file (without loading entire file),
validates dtype (bf16/fp16) and presence of weight_map.
Outputs table with results.

Usage:
    python scripts/weights/lint_safetensors.py --ckpt_dir checkpoints/oracle850b
"""

import argparse
import json
import sys
from pathlib import Path


def read_safetensors_header(file_path: Path) -> dict:
    """
    Reads safetensors file header.

    Args:
        file_path: Path to file.

    Returns:
        Dictionary with header metadata.

    Raises:
        ValueError: If file is not valid safetensors.
    """
    try:
        with open(file_path, "rb") as f:
            # Read first 1MB for header
            header_data = f.read(1024 * 1024)
            # Find end of header (JSON)
            header_end = header_data.find(b"\x00")
            if header_end == -1:
                raise ValueError("Invalid file format")
            header_json = header_data[:header_end].decode("utf-8")
            header = json.loads(header_json)
            return header
    except Exception as e:
        raise ValueError(f"Error reading header: {e}")


def lint_shard(file_path: Path, part_no: int) -> dict:
    """
    Lints single shard file.

    Args:
        file_path: Path to file.
        part_no: Part number.

    Returns:
        Dictionary with linting results.
    """
    size_bytes = file_path.stat().st_size

    try:
        header = read_safetensors_header(file_path)
    except ValueError as e:
        return {
            "part_no": part_no,
            "size_bytes": size_bytes,
            "dtype": "ERROR",
            "ok": False,
            "error": str(e),
        }

    # Check for weight_map presence
    if "__metadata__" not in header or "weight_map" not in header["__metadata__"]:
        return {
            "part_no": part_no,
            "size_bytes": size_bytes,
            "dtype": "UNKNOWN",
            "ok": False,
            "error": "Missing weight_map in metadata",
        }

    # Determine dtype (simplified check)
    dtype = "UNKNOWN"
    if "bf16" in str(header).lower():
        dtype = "bf16"
    elif "fp16" in str(header).lower():
        dtype = "fp16"

    return {
        "part_no": part_no,
        "size_bytes": size_bytes,
        "dtype": dtype,
        "ok": dtype in ["bf16", "fp16"],
        "error": None,
    }


def main():
    parser = argparse.ArgumentParser(description="Linting safetensors files")
    parser.add_argument(
        "--ckpt_dir",
        type=str,
        default="checkpoints/oracle850b",
        help="Path to checkpoints directory",
    )
    args = parser.parse_args()

    ckpt_path = Path(args.ckpt_dir)

    # Find shards
    shard_files = sorted(ckpt_path.glob("model-*-of-*.safetensors"))
    if not shard_files:
        print("Error: No shard files found")
        sys.exit(1)

    print("Linting shards:")
    print("part_no | size_bytes | dtype | ok")
    print("-" * 40)

    all_ok = True
    for i, shard_file in enumerate(shard_files, 1):
        result = lint_shard(shard_file, i)
        print(
            f"{result['part_no']"7"} | {result['size_bytes']"10"} | {result['dtype']"5"} | {'✓' if result['ok'] else '✗'}"
        )
        if not result['ok']:
            all_ok = False
            if result['error']:
                print(f"        Error: {result['error']}")

    print("-" * 40)
    if all_ok:
        print("All shards passed linting successfully")
        return 0
    else:
        print("Some shards have issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
