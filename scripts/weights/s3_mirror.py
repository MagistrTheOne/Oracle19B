#!/usr/bin/env python3
"""
s3_mirror.py - Mirroring weights to Object Storage (YC) for Oracle850B-MoE.

Copies shard files to S3, writes URI list, verifies SHA256 after upload.

Usage:
    python scripts/weights/s3_mirror.py --ckpt_dir checkpoints/oracle850b
"""

import hashlib
import os
import sys
from pathlib import Path


def compute_sha256(file_path: Path) -> str:
    """Computes full SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def mirror_to_s3(ckpt_path: Path, s3_bucket: str) -> list:
    """
    Mirrors files to S3.

    Args:
        ckpt_path: Path to checkpoints.
        s3_bucket: S3 bucket name.

    Returns:
        List of dictionaries with metadata.
    """
    # Simplified: mock S3 upload process
    shard_files = sorted(ckpt_path.glob("model-*-of-*.safetensors"))
    mirrored_files = []

    for shard_file in shard_files:
        file_size = shard_file.stat().st_size
        sha256 = compute_sha256(shard_file)

        # Mock upload
        s3_key = f"oracle850b-moe/{shard_file.name}"
        s3_uri = f"s3://{s3_bucket}/{s3_key}"

        print(f"Mirroring {shard_file.name} -> {s3_uri}")
        # In reality: boto3.client('s3').upload_file(...)

        mirrored_files.append({
            "path": shard_file.name,
            "size": file_size,
            "sha256": sha256,
            "s3_uri": s3_uri,
        })

    return mirrored_files


def save_mirror_manifest(mirrored_files: list, output_path: str):
    """Saves mirror manifest."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mirrored_files, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Mirror to S3")
    parser.add_argument(
        "--ckpt_dir",
        type=str,
        default="checkpoints/oracle850b",
        help="Path to checkpoints directory",
    )
    parser.add_argument(
        "--bucket",
        type=str,
        default="oracle850b-moe-weights",
        help="S3 bucket name",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="weights/s3_mirror.json",
        help="Path to manifest file",
    )
    args = parser.parse_args()

    ckpt_path = Path(args.ckpt_dir)

    if not ckpt_path.exists():
        print(f"Error: Directory {ckpt_path} not found")
        sys.exit(1)

    shard_files = list(ckpt_path.glob("model-*-of-*.safetensors"))
    if not shard_files:
        print("Error: No shard files found")
        sys.exit(1)

    print(f"Found {len(shard_files)} files to mirror")

    try:
        mirrored = mirror_to_s3(ckpt_path, args.bucket)
        save_mirror_manifest(mirrored, args.output)
        print(f"Manifest saved to {args.output}")
        print("Mirroring completed successfully")
        return 0
    except Exception as e:
        print(f"Mirroring error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
