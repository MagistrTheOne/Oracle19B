# Oracle19B - DEPRECATED

> **⚠️ DEPRECATED**: This project has been migrated to **Oracle850B-MoE**
> 
> **New Repository**: [MagistrTheOne/oracle850b-moe](https://github.com/MagistrTheOne/oracle850b-moe)
> 
> **Migration Date**: 2025-01-XX
> 
> **Reason**: Architecture upgrade to Mixture of Experts (MoE) with 850B parameters

## What happened?

The Oracle19B project has been **deprecated** and **migrated** to a new architecture:

- **Old**: Oracle19B (19B parameters, dense architecture)
- **New**: Oracle850B-MoE (850B parameters, Mixture of Experts)

## Migration Guide

### For Users
1. **Update your imports**:
   ```python
   # Old
   from oracle19b import *
   
   # New
   from oracle.moe850b import *
   ```

2. **Update configuration paths**:
   ```bash
   # Old
   configs/model/oracle19b.json
   
   # New
   src/oracle/moe850b/configs/model/oracle850b.moe.json
   ```

3. **Update Hugging Face repository**:
   ```bash
   # Old
   MagistrTheOne/oracle19b
   
   # New
   MagistrTheOne/oracle850b-moe
   ```

### For Developers
1. **Clone the new repository**:
   ```bash
   git clone https://github.com/MagistrTheOne/oracle850b-moe.git
   cd oracle850b-moe
   ```

2. **Follow the new setup**:
   ```bash
   make bootstrap
   make ci-guards
   ```

## Key Changes

### Architecture
- **Model Type**: Dense → Mixture of Experts (MoE)
- **Parameters**: 19B → 850B (64 experts, top-k=2)
- **Active Parameters**: ~110-130B per token
- **Context Length**: 8K tokens
- **Special Tokens**: `<|oracle_sys|>`, `<|oracle_intro|>`, `<|author|>`

### Package Structure
```
oracle/
├─ src/oracle/
│  ├─ core/           # Common components
│  ├─ moe850b/        # MoE 850B model
│  ├─ tokenization/   # Tokenizer
│  └─ serve/          # FastAPI server
├─ infra/             # Infrastructure
├─ datasets/          # Data processing
└─ scripts/          # Utilities
```

### New Features
- **MoE Architecture**: 64 experts with top-k=2 routing
- **Load Balancing**: Expert capacity management
- **Flash Attention**: Optimized attention computation
- **RoPE**: Rotary Position Embeddings
- **RMSNorm**: Root Mean Square Layer Normalization

## Timeline

- **2025-01-XX**: Oracle19B deprecated
- **2025-01-XX**: Oracle850B-MoE released
- **2025-02-XX**: Oracle19B repository archived (planned)

## Support

- **New Issues**: [Oracle850B-MoE Issues](https://github.com/MagistrTheOne/oracle850b-moe/issues)
- **Documentation**: [Oracle850B-MoE Docs](https://github.com/MagistrTheOne/oracle850b-moe#readme)
- **Hugging Face**: [oracle850b-moe](https://huggingface.co/MagistrTheOne/oracle850b-moe)

## Author

**MagistrTheOne|Краснодар|2025**

---

*This repository is archived and no longer maintained. Please use Oracle850B-MoE for all new development.*
