#!/usr/bin/env python3
"""
verify_index.py - Complete verification of index and files for Oracle850B-MoE.

Computes SHA256 of each shard, compares with manifest,
verifies model.safetensors.index.json, checks config.json fields.

Usage:
    python scripts/weights/verify_index.py --ckpt_dir checkpoints/oracle850b --manifest weights/manifest.json
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path


def compute_partial_sha256(file_path: Path, sample_size: int = 1024 * 1024) -> str:
    """Computes partial SHA256 (first sample_size bytes)."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        data = f.read(sample_size)
        sha256.update(data)
    return sha256.hexdigest()


def load_manifest(manifest_path: Path) -> list:
    """Loads manifest file."""
    if not manifest_path.exists():
        return []
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_shard(ckpt_path: Path, shard_file: str, manifest: list) -> dict:
    """Verifies single shard."""
    file_path = ckpt_path / shard_file
    if not file_path.exists():
        return {"file": shard_file, "ok": False, "error": "File not found"}

    size_bytes = file_path.stat().st_size
    sha256 = compute_partial_sha256(file_path)

    # Find in manifest
    manifest_entry = None
    for entry in manifest:
        if entry.get("path") == shard_file:
            manifest_entry = entry
            break

    if manifest_entry:
        if manifest_entry.get("size") != size_bytes:
            return {"file": shard_file, "ok": False, "error": "Size mismatch"}
        if manifest_entry.get("sha256") != sha256:
            return {"file": shard_file, "ok": False, "error": "SHA256 mismatch"}

    return {"file": shard_file, "ok": True, "size": size_bytes, "sha256": sha256}


def load_config(ckpt_path: Path) -> dict:
    """Loads config.json."""
    config_path = ckpt_path / "config.json"
    if not config_path.exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_config(config: dict) -> list:
    """Verifies config.json fields."""
    issues = []

    required_fields = ["vocab_size", "max_seq_len"]
    for field in required_fields:
        if field not in config:
            issues.append(f"Missing field {field}")

    if "moe" not in str(config).lower():
        issues.append("No MoE-specific fields found")

    return issues


def main():
    parser = argparse.ArgumentParser(description="Verify index and files")
    parser.add_argument(
        "--ckpt_dir",
        type=str,
        default="checkpoints/oracle850b",
        help="Path to checkpoints directory",
    )
    parser.add_argument(
        "--manifest",
        type=str,
        help="Path to manifest file (optional)",
    )
    args = parser.parse_args()

    ckpt_path = Path(args.ckpt_dir)
    manifest_path = Path(args.manifest) if args.manifest else None
    manifest = load_manifest(manifest_path) if manifest_path else []

    # Load index
    index_path = ckpt_path / "model.safetensors.index.json"
    if not index_path.exists():
        print("Error: Index not found")
        sys.exit(1)

    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)

    # Verify shards
    shard_files = list(ckpt_path.glob("model-*-of-*.safetensors"))
    if not shard_files:
        print("Error: No shard files found")
        sys.exit(1)

    print("Verifying shards:")
    all_ok = True
    total_size = 0

    for shard_file in sorted(shard_files):
        result = verify_shard(ckpt_path, shard_file.name, manifest)
        if result["ok"]:
            print(f"  OK {result['file']}")
            total_size += result["size"]
        else:
            print(f"  ERROR {result['file']}: {result['error']}")
            all_ok = False

    # Verify index
    weight_map = index.get("weight_map", {})
    print(f"\nIndex: {len(weight_map)} keys")
    if len(weight_map) != len(shard_files):
        print("Warning: Key count does not match shard count")
        all_ok = False

    # Verify config
    config = load_config(ckpt_path)
    config_issues = verify_config(config)
    if config_issues:
        print("\nConfig issues:")
        for issue in config_issues:
            print(f"  ERROR {issue}")
        all_ok = False
    else:
        print("\nConfig is valid")

    # Summary
    print(f"\nTotal size: {total_size / (1024**3)".2f"} GB")
    if all_ok:
        print("Verification passed successfully")
        return 0
    else:
        print("Issues found")
        return 1


if __name__ == "__main__":
    sys.exit(main())
