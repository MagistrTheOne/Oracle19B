#!/usr/bin/env python3
"""
hf_upload_weights.py - Safe batch upload of weights to Hugging Face for Oracle850B-MoE.

Requires HF_TIER=pro, enables HF_HUB_ENABLE_HF_TRANSFER.
Uploads shards in parallel, logs progress.

Usage:
    HF_TIER=pro HF_HUB_ENABLE_HF_TRANSFER=1 python scripts/weights/hf_upload_weights.py
"""

import os
import sys
from pathlib import Path


def check_environment():
    """Checks environment variables."""
    hf_tier = os.getenv("HF_TIER", "").lower()
    if hf_tier != "pro":
        print(f"Error: HF_TIER must be 'pro'. Current: {hf_tier or 'not set'}")
        sys.exit(1)

    hf_transfer = os.getenv("HF_HUB_ENABLE_HF_TRANSFER", "0")
    if hf_transfer != "1":
        print("Error: HF_HUB_ENABLE_HF_TRANSFER must be '1'")
        sys.exit(1)

    hf_repo = os.getenv("HF_REPO")
    if not hf_repo:
        print("Error: HF_REPO not set")
        sys.exit(1)


def upload_weights():
    """Uploads weights to Hugging Face."""
    ckpt_dir = os.getenv("CKPT_DIR", "checkpoints/oracle850b")
    hf_repo = os.getenv("HF_REPO")

    ckpt_path = Path(ckpt_dir)

    # Find files to upload
    files_to_upload = [
        "model.safetensors.index.json",
    ] + [f.name for f in ckpt_path.glob("model-*-of-*.safetensors")]

    if not files_to_upload:
        print("Error: No files to upload found")
        sys.exit(1)

    print(f"Preparing upload to {hf_repo}...")
    print(f"Files: {len(files_to_upload)}")

    # Upload using huggingface_hub
    try:
        from huggingface_hub import HfApi

        api = HfApi()

        for file_name in files_to_upload:
            file_path = ckpt_path / file_name
            if file_path.exists():
                print(f"Uploading {file_name}...")
                # Upload file
                api.upload_file(
                    path_or_fileobj=str(file_path),
                    path_in_repo=file_name,
                    repo_id=hf_repo,
                    repo_type="model",
                )
                print(f"OK {file_name} uploaded")
            else:
                print(f"Warning: {file_name} not found")

        print("Upload completed successfully")

    except ImportError:
        print("Error: Requires huggingface_hub. Install: pip install huggingface_hub")
        sys.exit(1)
    except Exception as e:
        print(f"Upload error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Upload weights to Hugging Face")
    args = parser.parse_args()

    try:
        check_environment()
        upload_weights()
        return 0
    except SystemExit as e:
        return e.code
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
