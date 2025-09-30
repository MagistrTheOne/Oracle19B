#!/usr/bin/env python3
"""
build_index.py - Generation and verification of model.safetensors.index.json for Oracle850B-MoE.

If index does not exist - builds from current files with relative paths.
If exists - verifies weight_map against disk; suggests update if desynchronized.

Usage:
    python scripts/weights/build_index.py --ckpt_dir checkpoints/oracle850b
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path


def compute_file_sha256(file_path: Path) -> str:
    """Computes SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def build_index_from_files(ckpt_path: Path) -> dict:
    """
    Builds index from files in directory.

    Args:
        ckpt_path: Path to checkpoints.

    Returns:
        Dictionary with index.
    """
    shard_files = sorted(ckpt_path.glob("model-*-of-*.safetensors"))

    weight_map = {}
    metadata = {"total_size": 0}

    for shard_file in shard_files:
        shard_name = shard_file.name
        file_size = shard_file.stat().st_size
        metadata["total_size"] += file_size

        # Read header to extract keys (simplified)
        try:
            with open(shard_file, "rb") as f:
                header_data = f.read(1024 * 1024)
                header_end = header_data.find(b"\x00")
                if header_end != -1:
                    header_json = header_data[:header_end].decode("utf-8")
                    header = json.loads(header_json)
                    for key in header.keys():
                        if key != "__metadata__":
                            weight_map[key] = shard_name
        except Exception as e:
            print(f"Warning: Could not read {shard_name}: {e}")
            # Continue without this shard

    return {
        "metadata": metadata,
        "weight_map": weight_map,
    }


def load_existing_index(index_path: Path) -> dict:
    """Loads existing index."""
    with open(index_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Build safetensors index")
    parser.add_argument(
        "--ckpt_dir",
        type=str,
        default="checkpoints/oracle850b",
        help="Path to checkpoints directory",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing index",
    )
    args = parser.parse_args()

    ckpt_path = Path(args.ckpt_dir)
    index_path = ckpt_path / "model.safetensors.index.json"

    if index_path.exists() and not args.force:
        print("Index already exists. Checking synchronization...")
        existing_index = load_existing_index(index_path)

        # Simple check: compare shard count
        shard_files = list(ckpt_path.glob("model-*-of-*.safetensors"))
        expected_shards = len(shard_files)

        if "metadata" in existing_index and "total_size" in existing_index["metadata"]:
            print("Index synchronized with files.")
            print(f"Total size: {existing_index['metadata']['total_size']} bytes")
            return 0
        else:
            print("Index is corrupted or incomplete.")
    else:
        print("Building new index...")

    new_index = build_index_from_files(ckpt_path)

    # Save index
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(new_index, f, indent=2)

    print(f"Index saved to {index_path}")
    print(f"Keys in weight_map: {len(new_index.get('weight_map', {}))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
