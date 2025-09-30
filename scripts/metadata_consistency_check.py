#!/usr/bin/env python3
"""
Metadata Consistency Check

Validates that README.md and MODEL_CARD.md contain the same architecture
values as configs/model/oracle850b.moe.json.

Usage:
    python scripts/metadata_consistency_check.py

Can be used as a git pre-commit hook or CI step.

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


def extract_canonical_values(config):
    """Extract canonical values from config for validation."""
    return {
        'experts': config['moe']['experts'],
        'expert_hidden': config['moe']['expert_hidden'],
        'd_model': config['dense']['d_model'],
        'n_layers': config['dense']['n_layers'],
        'n_heads': config['dense']['n_heads'],
        'd_ff': config['dense']['d_ff'],
        'vocab_size': config['vocab_size'],
        'max_seq_len': config['max_seq_len'],
    }


def check_file(file_path, canonical_values):
    """Check if a file contains all canonical values."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
        return False

    missing_values = []

    for key, value in canonical_values.items():
        # Convert value to string for searching (handles both int and float)
        value_str = str(value)
        if value_str not in content:
            missing_values.append(f"{key}: {value}")

    if missing_values:
        print(f"[ERROR] {file_path.name}: Missing values: {', '.join(missing_values)}")
        return False
    else:
        print(f"[OK] {file_path.name}: All values present")
        return True


def check_widget_identity():
    """Check that MODEL_CARD.md has the correct English widget."""
    model_card_path = Path(__file__).parent.parent / "MODEL_CARD.md"

    try:
        with open(model_card_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("[ERROR] MODEL_CARD.md not found")
        return False

    # Check for correct English widget text
    correct_widget = "I am Oracle850B-MoE. Author: MagistrTheOne|Krasnodar|2025. Ready."
    if correct_widget in content:
        print("[OK] MODEL_CARD.md: Correct English widget found")
        return True
    else:
        print("[ERROR] MODEL_CARD.md: English widget not found or incorrect")
        return False


def main():
    """Main validation function."""
    print("[INFO] Running metadata consistency checks...")

    # Read canonical config
    try:
        config = read_config()
    except FileNotFoundError:
        print("[ERROR] Config file not found: configs/model/oracle850b.moe.json")
        return 1
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in config: {e}")
        return 1

    # Extract canonical values
    canonical_values = extract_canonical_values(config)

    # Check files
    files_to_check = [
        Path(__file__).parent.parent / "README.md",
        Path(__file__).parent.parent / "MODEL_CARD.md"
    ]

    all_files_ok = True

    for file_path in files_to_check:
        if not check_file(file_path, canonical_values):
            all_files_ok = False

    # Check widget identity
    if not check_widget_identity():
        all_files_ok = False

    # Summary
    if all_files_ok:
        print("\n[SUCCESS] All metadata consistency checks passed!")
        return 0
    else:
        print("\n[ERROR] Some metadata consistency checks failed!")
        print("[HINT] Run 'python scripts/sync_arch_snippet.py' to fix")
        return 1


if __name__ == "__main__":
    sys.exit(main())
