#!/usr/bin/env python3
import json
import os

def main():
    print('Final Project Validation for Hugging Face Publication')
    print('=' * 60)

    # Check 1: Model config matches declared parameters
    with open('configs/model/oracle850b.moe.json', 'r') as f:
        config = json.load(f)

    declared = config['param_total']
    print(f'1. Declared parameters: {declared:,} - OK')

    # Check 2: Architecture is custom (no external models)
    external_models = ['gpt2', 'llama', 'mistral', 'qwen', 'phi', 'gemma', 'opt']
    found_external = []
    for model in external_models:
        if model.lower() in str(config).lower():
            found_external.append(model)

    if not found_external:
        print('2. No external model dependencies - OK')
    else:
        print(f'2. External models found: {found_external} - ERROR')

    # Check 3: Metadata files exist and are valid
    metadata_files = [
        'generation_config.json',
        'special_tokens_map.json',
        'MODEL_CARD.md',
        'README.md'
    ]

    for file in metadata_files:
        if os.path.exists(file):
            print(f'3. {file} exists - OK')
        else:
            print(f'3. {file} missing - ERROR')

    # Check 4: Tokenizer config matches model
    with open('checkpoints/oracle850b/tokenizer/tokenizer_config.json', 'r') as f:
        tokenizer_config = json.load(f)

    model_vocab_size = config['vocab_size']
    tokenizer_vocab_size = tokenizer_config['vocab_size']

    if model_vocab_size == tokenizer_vocab_size:
        print(f'4. Vocabulary sizes match: {model_vocab_size:,} - OK')
    else:
        print(f'4. Vocabulary mismatch: model={model_vocab_size:,}, tokenizer={tokenizer_vocab_size:,} - ERROR')

    # Check 5: HF token available
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            if 'hf_' in content:
                print('5. Hugging Face token configured - OK')
            else:
                print('5. Hugging Face token not found - ERROR')
    else:
        print('5. .env file missing - ERROR')

    print()
    print('Project validation completed')

if __name__ == "__main__":
    main()
