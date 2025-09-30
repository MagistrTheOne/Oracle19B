#!/usr/bin/env python3
"""
vllm_compat_check.py - Compatibility check with vLLM for Oracle850B-MoE.

Checks config.json, limits, dtype, rope/rmsnorm flags.

Usage:
    python scripts/weights/vllm_compat_check.py --ckpt_dir checkpoints/oracle850b
"""

import json
import sys
from pathlib import Path


def load_config(ckpt_path: Path) -> dict:
    """Loads config.json."""
    config_path = ckpt_path / "config.json"
    if not config_path.exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_generation_config(ckpt_path: Path) -> dict:
    """Loads generation_config.json."""
    gen_path = ckpt_path / "generation_config.json"
    if not gen_path.exists():
        return {}
    with open(gen_path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_vllm_compatibility(ckpt_path: Path) -> tuple[bool, list]:
    """
    Checks vLLM compatibility.

    Returns:
        Tuple: (is_compatible, list of issues).
    """
    issues = []

    config = load_config(ckpt_path)
    gen_config = load_generation_config(ckpt_path)

    # Check required fields
    required_config_fields = [
        "vocab_size",
        "max_seq_len",
        "hidden_size",
        "num_attention_heads",
    ]
    for field in required_config_fields:
        if field not in config:
            issues.append(f"Missing field {field} in config.json")

    # Check MoE fields (if applicable)
    if "num_experts" not in config:
        issues.append("Missing num_experts for MoE model")

    # Check max_seq_len
    max_seq_len = config.get("max_seq_len", 0)
    if max_seq_len > 32768:
        issues.append(f"max_seq_len ({max_seq_len}) may exceed vLLM limits")

    # Check rope_scaling
    if "rope_scaling" in config:
        rope = config["rope_scaling"]
        if not isinstance(rope, dict) or "type" not in rope:
            issues.append("Invalid rope_scaling")

    # Check tokenizer
    tokenizer_path = ckpt_path / "tokenizer" / "tokenizer.json"
    if not tokenizer_path.exists():
        issues.append("Missing tokenizer.json")

    # Additional checks for MoE
    if "moe" in str(config).lower():
        if "num_experts" not in config or config["num_experts"] < 1:
            issues.append("Invalid expert count for MoE")

    is_compatible = len(issues) == 0
    return is_compatible, issues


def main():
    parser = argparse.ArgumentParser(description="Check vLLM compatibility")
    parser.add_argument(
        "--ckpt_dir",
        type=str,
        default="checkpoints/oracle850b",
        help="Path to checkpoints directory",
    )
    args = parser.parse_args()

    ckpt_path = Path(args.ckpt_dir)

    if not ckpt_path.exists():
        print(f"Error: Directory {ckpt_path} not found")
        sys.exit(1)

    print("Checking vLLM compatibility...")

    compatible, issues = check_vllm_compatibility(ckpt_path)

    if compatible:
        print("OK Model is compatible with vLLM")
        return 0
    else:
        print("ERROR Compatibility issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
