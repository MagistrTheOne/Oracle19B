# Oracle850B-MoE Release Instructions

## 🚀 GitHub Release Process

### 1. Pre-Release Checklist
```bash
# Verify environment
make bootstrap
make ci-guards
make test

# Check infrastructure
make infra-plan
make helm-lint
make argo-dryrun

# Verify no external models
rg -n "gpt2|llama|mistral|qwen|phi|gemma|opt" -S . || echo "✅ No external models"
```

### 2. Create Release Branch
```bash
# Create and switch to release branch
git checkout -b release/oracle850b-moe

# Verify all changes are committed
git status
git add -A
git commit -m "refactor: oracle19b→oracle850b-moe; infra & docs

- New package structure: oracle.core, oracle.moe850b, oracle.serve
- MoE architecture: 64 experts, top-k=2, 850B parameters
- Infrastructure: Terraform/Helm/Argo with project naming
- VENV policy: strict isolation with .venv
- CI guards: ripgrep + venv enforcement
- Documentation: README, MODEL_CARD, RELEASE_NOTES
- Archive: oracle19b deprecated with migration guide

Author: MagistrTheOne|Краснодар|2025"

# Push release branch
git push origin release/oracle850b-moe
```

### 3. Create Pull Request
```bash
# Create PR from release branch to main
# Title: "Release: Oracle850B-MoE v0.1.0"
# Description: See RELEASE_NOTES.md
# Reviewers: [Add reviewers]
# Labels: release, major
```

### 4. Merge and Tag
```bash
# After PR approval and merge
git checkout main
git pull origin main

# Create and push tag
git tag -a v0.1.0-oracle850b -m "Oracle850B-MoE Initial Release

- MoE architecture with 850B parameters
- 64 experts, top-k=2 routing
- Custom tokenizer and special tokens
- Infrastructure for Yandex Cloud
- VENV policy and CI guards
- Migration from Oracle19B

Author: MagistrTheOne|Краснодар|2025"

git push origin v0.1.0-oracle850b
```

## 📦 Hugging Face Hub Release

### 1. Prepare HF Environment
```bash
# Install HF CLI
pip install -U "huggingface_hub[cli]"

# Login to HF
hf auth login
# Enter your HF token when prompted

# Verify login
hf whoami
```

### 2. Upload Metadata
```bash
# Set environment variables
export HF_REPO=MagistrTheOne/oracle850b-moe
export HUGGINGFACE_TOKEN=<YOUR_HF_TOKEN>

# Upload using script
python scripts/hf_upload.py

# Or upload manually
hf upload $HF_REPO . \
  --include "README.md" \
  --include "MODEL_CARD.md" \
  --include "RELEASE_NOTES.md" \
  --include "src/oracle/moe850b/configs/**" \
  --include "checkpoints/oracle850b/**" \
  --include ".gitattributes" \
  --exclude "*.pyc" \
  --exclude "__pycache__" \
  --exclude ".venv" \
  --exclude "*.bin" \
  --exclude "*.safetensors"
```

### 3. Verify Upload
```bash
# Check repository
hf repo info $HF_REPO

# List files
hf ls $HF_REPO

# Verify model card
hf repo info $HF_REPO --type=model
```

## 🗂️ Archive Oracle19B

### 1. Update Oracle19B Repository
```bash
# Clone old repository (if needed)
git clone https://github.com/MagistrTheOne/oracle19b.git
cd oracle19b

# Add deprecation notice
echo "# Oracle19B - DEPRECATED

> **⚠️ DEPRECATED**: This project has been migrated to **Oracle850B-MoE**
> 
> **New Repository**: [MagistrTheOne/oracle850b-moe](https://github.com/MagistrTheOne/oracle850b-moe)
> 
> **Migration Date**: $(date +%Y-%m-%d)
> 
> **Reason**: Architecture upgrade to Mixture of Experts (MoE) with 850B parameters

## Quick Migration

\`\`\`bash
# Clone new repository
git clone https://github.com/MagistrTheOne/oracle850b-moe.git
cd oracle850b-moe

# Setup
make bootstrap
make ci-guards
\`\`\`

## Key Changes

- **Architecture**: Dense → MoE (850B parameters)
- **Package**: \`oracle19b.*\` → \`oracle.*\`
- **Repository**: \`oracle19b\` → \`oracle850b-moe\`
- **HF Hub**: \`oracle19b\` → \`oracle850b-moe\`

**Author**: MagistrTheOne|Краснодар|2025" > README.md

# Commit and push
git add README.md
git commit -m "deprecate: migrate to Oracle850B-MoE"
git push origin main
```

### 2. Archive Repository (Optional)
```bash
# Archive repository (GitHub settings)
# 1. Go to repository settings
# 2. Scroll to "Danger Zone"
# 3. Click "Archive this repository"
# 4. Confirm archiving
```

## ✅ Post-Release Verification

### 1. GitHub Verification
- [ ] Release branch merged
- [ ] Tag v0.1.0-oracle850b created
- [ ] Release notes published
- [ ] Oracle19B deprecated

### 2. HF Hub Verification
- [ ] Repository created: MagistrTheOne/oracle850b-moe
- [ ] Metadata uploaded (configs, tokenizer, docs)
- [ ] Model card published
- [ ] Repository public and accessible

### 3. Documentation Verification
- [ ] README.md updated
- [ ] MODEL_CARD.md current
- [ ] RELEASE_NOTES.md complete
- [ ] Archive README.md redirects properly

### 4. Infrastructure Verification
- [ ] Terraform validates: `make infra-plan`
- [ ] Helm charts lint: `make helm-lint`
- [ ] Argo workflows validate: `make argo-dryrun`
- [ ] CI guards pass: `make ci-guards`

## 🔄 Rollback Plan

### If Issues Found
```bash
# Revert tag
git tag -d v0.1.0-oracle850b
git push origin :v0.1.0-oracle850b

# Revert merge (if needed)
git revert -m 1 <merge-commit-hash>
git push origin main

# Update HF repository
hf repo update $HF_REPO --private
```

### Emergency Contacts
- **Author**: MagistrTheOne|Краснодар|2025
- **Repository**: [oracle850b-moe](https://github.com/MagistrTheOne/oracle850b-moe)
- **Issues**: [GitHub Issues](https://github.com/MagistrTheOne/oracle850b-moe/issues)

---

**Note**: This is a major release with architectural changes. Test thoroughly before production use.
