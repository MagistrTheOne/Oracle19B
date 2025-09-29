# Oracle850B-MoE Release Notes

## v0.1.0-oracle850b - Initial MoE Release

**Release Date**: 2025-01-XX  
**Author**: MagistrTheOne|Краснодар|2025

### 🎉 Major Changes

#### Architecture Migration
- **FROM**: Oracle19B (19B parameters, dense architecture)
- **TO**: Oracle850B-MoE (850B parameters, Mixture of Experts)
- **Improvement**: 45x parameter increase with efficient expert routing

#### New MoE Architecture
- **Total Parameters**: 850B (64 experts)
- **Active Parameters**: ~110-130B per token (top-k=2)
- **Context Length**: 8192 tokens
- **Vocabulary**: 65536 tokens
- **Precision**: bf16 training, auto inference

#### Package Restructure
```
oracle/
├─ src/oracle/
│  ├─ core/           # Common components (attention, mlp, norm, rope)
│  ├─ moe850b/        # MoE 850B model and configs
│  ├─ tokenization/   # Custom tokenizer
│  └─ serve/          # FastAPI server
├─ infra/             # Infrastructure (Terraform/Helm/Argo)
├─ datasets/          # Data processing pipeline
└─ scripts/           # Utilities and tools
```

### 🚀 New Features

#### MoE Components
- **Expert Routing**: Top-k=2 selection with load balancing
- **Capacity Management**: Dynamic expert capacity allocation
- **Load Balancing Loss**: Prevents expert collapse
- **Flash Attention**: Optimized attention computation
- **RoPE**: Rotary Position Embeddings
- **RMSNorm**: Root Mean Square Layer Normalization

#### Infrastructure
- **Terraform**: Yandex Cloud with project naming
- **Helm**: Kubernetes charts for training/serving
- **Argo**: Workflow orchestration
- **Kill Switch**: Emergency resource shutdown

#### Data Pipeline
- **Ingest**: S3/HTTPS data collection
- **Clean**: Deduplication, language detection, PII removal
- **Decontaminate**: Evaluation set contamination removal
- **Shard**: WebDataset format with 512MB shards
- **Stats**: Quality assessment and reporting

### 🔧 Technical Improvements

#### VENV Policy
- **Strict Isolation**: All dependencies in `.venv`
- **Locked Versions**: `requirements.lock` for reproducibility
- **Bootstrap Script**: Automated setup with validation
- **CI Enforcement**: Fails if not using venv

#### CI/CD Enhancements
- **Ripgrep Guards**: Fast external model detection
- **VENV Enforcement**: Virtual environment validation
- **Architecture Checks**: Oracle850B component verification
- **HF Hub Integration**: Automated metadata upload

#### Security
- **NO LOCAL TRAIN**: `ALLOW_LOCAL_TRAIN=false` enforcement
- **NO EXTERNAL WEIGHTS**: Prohibited model references
- **OWN ARCHITECTURE**: Custom MoE implementation only

### 📦 Hugging Face Hub

#### Repository Migration
- **FROM**: `MagistrTheOne/oracle19b`
- **TO**: `MagistrTheOne/oracle850b-moe`
- **Status**: Metadata uploaded, weights pending training

#### Available Artifacts
- ✅ Model configuration (`oracle850b.moe.json`)
- ✅ Training configuration (`oracle850b.yaml`)
- ✅ Tokenizer configuration
- ✅ Default prompts and system messages
- ✅ Model card and documentation
- ⏳ Model weights (after cluster training)

### 🗂️ Deprecation Notice

#### Oracle19B Status
- **Status**: DEPRECATED
- **Migration**: Required to Oracle850B-MoE
- **Timeline**: 
  - 2025-01-XX: Deprecation announced
  - 2025-02-XX: Repository archived (planned)

#### Breaking Changes
- **Package Structure**: `oracle19b.*` → `oracle.*`
- **Configuration Paths**: `configs/` → `src/oracle/moe850b/configs/`
- **Import Statements**: Updated namespace
- **HF Repository**: New repository URL

### 🚀 Getting Started

#### Quick Setup
```bash
# Clone new repository
git clone https://github.com/MagistrTheOne/oracle850b-moe.git
cd oracle850b-moe

# Bootstrap environment
make bootstrap

# Verify setup
make ci-guards

# Run data pipeline (dry-run)
make prep-tb
```

#### Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with your values
nano .env

# Key variables:
# HF_REPO=MagistrTheOne/oracle850b-moe
# HUGGINGFACE_TOKEN=hf_***
# ALLOW_LOCAL_TRAIN=false
```

### 📋 Migration Checklist

#### For Users
- [ ] Update repository URL
- [ ] Update import statements
- [ ] Update configuration paths
- [ ] Test new setup with `make bootstrap`

#### For Developers
- [ ] Review new package structure
- [ ] Update CI/CD pipelines
- [ ] Update infrastructure configurations
- [ ] Test MoE components

### 🔮 Roadmap

#### Short Term (Q1 2025)
- [ ] Cluster training completion
- [ ] Model weights release
- [ ] Performance benchmarks
- [ ] Documentation updates

#### Medium Term (Q2 2025)
- [ ] 32K context length support
- [ ] Multi-modal capabilities
- [ ] Advanced routing strategies
- [ ] Production optimizations

#### Long Term (Q3-Q4 2025)
- [ ] 1T+ parameter scaling
- [ ] Specialized expert domains
- [ ] Cross-lingual capabilities
- [ ] Enterprise features

### 🐛 Known Issues

#### Current Limitations
- Model weights not yet available (training in progress)
- Limited to 8K context length (32K planned)
- Requires significant computational resources
- Expert routing may need tuning

#### Workarounds
- Use metadata-only setup for development
- Implement custom expert routing if needed
- Monitor resource usage during training
- Follow load balancing best practices

### 📞 Support

#### Resources
- **Repository**: [oracle850b-moe](https://github.com/MagistrTheOne/oracle850b-moe)
- **Hugging Face**: [oracle850b-moe](https://huggingface.co/MagistrTheOne/oracle850b-moe)
- **Issues**: [GitHub Issues](https://github.com/MagistrTheOne/oracle850b-moe/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MagistrTheOne/oracle850b-moe/discussions)

#### Contact
- **Author**: MagistrTheOne|Краснодар|2025
- **Email**: [Contact information to be provided]
- **Support**: [GitHub Issues](https://github.com/MagistrTheOne/oracle850b-moe/issues)

---

**Note**: This is a major architectural upgrade. Please review all changes carefully and test thoroughly before production use.
