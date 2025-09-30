# Oracle850B-MoE Model Weights

## Overview

This document describes the model weights structure, validation procedures, and deployment information for Oracle850B-MoE.

## Model Specifications

- **Model Name**: Oracle850B-MoE
- **Architecture**: Mixture of Experts (MoE) Transformer
- **Total Parameters**: 850 billion
- **Active Parameters per Token**: 180-220 billion (top-k=2)
- **Context Length**: 16,384 tokens
- **Vocabulary Size**: 131,072 tokens

## Architecture Details

### Dense Component
- **Model Dimension**: 8,192
- **Layers**: 96
- **Attention Heads**: 64
- **Feed-Forward Dimension**: 24,576

### MoE Component
- **Number of Experts**: 128
- **Expert Hidden Multiplier**: 4.0
- **Router Type**: Top-k (k=2)
- **Load Balancing Loss**: 0.01

## File Structure

```
checkpoints/oracle850b/
├── config.json                    # Model configuration
├── generation_config.json         # Generation parameters
├── tokenizer/                     # Tokenizer files
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   └── special_tokens_map.json
├── model.safetensors.index.json   # Weight shards index
├── model-00001-of-00128.safetensors
├── model-00002-of-00128.safetensors
└── ... (126 more shards)
```

## Shard Information

- **Total Shards**: 128
- **Format**: SafeTensors
- **Naming Convention**: model-XXXXX-of-00128.safetensors
- **Max Shard Size**: 2GB
- **Index File**: model.safetensors.index.json

## Validation Procedures

### 1. Structure Verification
```bash
python scripts/weights/collect_drop.py --ckpt_dir checkpoints/oracle850b
```

### 2. SafeTensors Linting
```bash
python scripts/weights/lint_safetensors.py --ckpt_dir checkpoints/oracle850b
```

### 3. Index Building/Verification
```bash
python scripts/weights/build_index.py --ckpt_dir checkpoints/oracle850b
python scripts/weights/verify_index.py --ckpt_dir checkpoints/oracle850b --manifest weights/manifest.json
```

### 4. Manifest Generation
```bash
make weights-manifest
```

## Deployment Information

### Minimum Requirements
- **GPUs**: 16+ (H100/A100 preferred)
- **Memory per GPU**: 80GB
- **Total Memory**: 1.28TB minimum
- **Network**: High-speed interconnect (InfiniBand)

### Recommended Setup
- **GPUs**: 32x H100-80GB
- **Tensor Parallel**: 16
- **Pipeline Parallel**: 12
- **Sequence Parallel**: Enabled

### Inference Memory Usage
- **Full Model**: ~850GB VRAM
- **Active Parameters**: ~180GB per forward pass
- **KV Cache**: Scales with batch size and sequence length

## Performance Characteristics

### Efficiency
- **Active Parameters**: 180-220B per token
- **Quality**: Comparable to 200B+ dense models
- **Speed**: Optimized with expert routing
- **Memory**: Efficient usage through MoE architecture

### Training Metrics
- **Training Steps**: 800,000
- **Batch Size**: 4,096 global
- **Learning Rate**: 8e-5
- **Precision**: BF16 mixed precision

## Security Considerations

### Weight Integrity
- All shards validated with SHA256 checksums
- Manifest file contains size and hash information
- Index file verified against actual files

### Access Control
- Model weights require appropriate permissions
- Repository access controlled via Hugging Face Hub
- Private repositories for sensitive configurations

## Troubleshooting

### Common Issues
1. **Missing Shards**: Verify all 128 shards are present
2. **Corrupted Files**: Re-download and re-validate
3. **Memory Issues**: Reduce batch size or use gradient checkpointing
4. **Loading Errors**: Check SafeTensors format compliance

### Support
- **Repository**: https://github.com/MagistrTheOne/oracle850b-moe
- **Issues**: Report via GitHub Issues
- **Documentation**: See MODEL_CARD.md for detailed information
