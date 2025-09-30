#!/usr/bin/env python3
"""
Sync Architecture Snippets Across Files

Reads configs/model/oracle850b.moe.json and updates architecture JSON blocks
in README.md and MODEL_CARD.md to ensure consistency.

Usage:
    python scripts/sync_arch_snippet.py

Author: MagistrTheOne|Krasnodar|2025
"""

import json
import re
import sys
from pathlib import Path


def read_config():
    """Read the canonical model configuration."""
    config_path = Path(__file__).parent.parent / "configs" / "model" / "oracle850b.moe.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_json_snippet(config):
    """Format the canonical JSON snippet for insertion."""
    canonical = {
        "model_name": config["model_name"],
        "arch": config["arch"],
        "param_total": config["param_total"],
        "moe": {
            "experts": config["moe"]["experts"],
            "expert_hidden": config["moe"]["expert_hidden"],
            "router": config["moe"]["router"]
        },
        "dense": config["dense"],
        "activation": config["activation"],
        "rope_theta": config["rope_theta"],
        "rotary_pct": config["rotary_pct"],
        "rmsnorm_eps": config["rmsnorm_eps"],
        "flash_attn": config["flash_attn"],
        "kv_cache": config["kv_cache"],
        "vocab_size": config["vocab_size"],
        "max_seq_len": config["max_seq_len"],
        "fp": config["fp"]
    }

    return json.dumps(canonical, indent=2)


def update_file(file_path, new_json):
    """Update a file with the new JSON snippet."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match JSON blocks in markdown
    json_pattern = r'```json\s*\n(\{[\s\S]*?\})\s*\n```'

    def replace_json(match):
        return f'```json\n{new_json}\n```'

    updated_content = re.sub(json_pattern, replace_json, content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    return content != updated_content


def main():
    """Main sync function."""
    print("[INFO] Syncing architecture snippets...")

    # Read canonical config
    config = read_config()

    # Format canonical JSON
    canonical_json = format_json_snippet(config)

    # Update files
    files_to_update = [
        Path(__file__).parent.parent / "README.md",
        Path(__file__).parent.parent / "MODEL_CARD.md"
    ]

    updated_files = []

    for file_path in files_to_update:
        if file_path.exists():
            if update_file(file_path, canonical_json):
                updated_files.append(file_path.name)
                print(f"[OK] Updated {file_path.name}")
            else:
                print(f"[OK] {file_path.name} already up to date")
        else:
            print(f"[ERROR] File not found: {file_path}")
            return 1

    if updated_files:
        print(f"\n[INFO] Updated files: {', '.join(updated_files)}")
        print("[HINT] Run metadata consistency check to verify")
    else:
        print("\n[OK] All files already have correct architecture snippets")

    return 0


if __name__ == "__main__":
    sys.exit(main())
