#!/bin/bash
# Oracle850B Bootstrap Script
# Strict venv isolation for Oracle850B
# Author: MagistrTheOne|Краснодар|2025

set -euo pipefail

echo "🚀 Oracle850B Bootstrap - Strict VENV Isolation"
echo "=============================================="

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo "❌ Python $required_version+ required, found $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create venv
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Activate venv
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip and wheel
echo "⬆️  Upgrading pip and wheel..."
pip install -U pip wheel

# Install dependencies
echo "📚 Installing dependencies..."

if [[ -f "requirements.lock" ]]; then
    echo "  Using locked dependencies..."
    pip install -r requirements.lock
else
    echo "  Using requirements.in, will create lock file..."
    pip install -r requirements.in
    pip freeze > requirements.lock
    echo "✅ Created requirements.lock"
fi

# Verify installation
echo "🔍 Verifying installation..."
python -c "
import sys
import os
assert os.getenv('VIRTUAL_ENV'), 'VENV not activated'
assert '.venv' in sys.executable, 'Not using venv Python'
print('✅ Virtual environment verified')
"

# Check for external models
echo "🛡️  Checking for external models..."
if grep -r -i "gpt2\|llama\|mistral\|qwen\|phi\|gemma\|opt" --include="*.py" --include="*.json" --include="*.yaml" .; then
    echo "❌ External model references found!"
    exit 1
fi

echo "✅ No external models found"

# Run basic tests
echo "🧪 Running basic tests..."
python -c "
import sys
sys.path.append('src')
from oracle import __version__
print(f'✅ Oracle package version: {__version__}')
"

echo ""
echo "🎉 Bootstrap completed successfully!"
echo "💡 To activate: source .venv/bin/activate"
echo "💡 To sync: make sync"
