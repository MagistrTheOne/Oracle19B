#!/usr/bin/env python3
import json

def main():
    # Load model config
    with open('configs/model/oracle850b.moe.json', 'r') as f:
        config = json.load(f)

    # Current config
    vocab_size = config['vocab_size']
    d_model = config['dense']['d_model']
    n_layers = config['dense']['n_layers']
    d_ff = config['dense']['d_ff']
    n_experts = config['moe']['experts']
    expert_mult = config['moe']['expert_hidden_mult']

    print('Current config:')
    print(f'  d_model: {d_model:,}')
    print(f'  n_layers: {n_layers}')
    print(f'  d_ff: {d_ff:,}')
    print(f'  n_experts: {n_experts}')
    print(f'  expert_mult: {expert_mult}')
    print()

    # Calculate with current numbers
    embed_params = vocab_size * d_model
    attn_params_per_layer = 4 * (d_model * d_model)  # Q,K,V,O
    ffn_params_per_layer = 2 * (d_model * d_ff)
    dense_layer_params = attn_params_per_layer + ffn_params_per_layer
    dense_total = n_layers * dense_layer_params

    expert_dim = int(d_ff * expert_mult)
    expert_params = 2 * (d_model * expert_dim)
    moe_total = n_experts * expert_params

    output_params = d_model * vocab_size

    total = embed_params + dense_total + moe_total + output_params
    print(f'Calculated: {total:,}')
    print(f'Declared: {config["param_total"]:,}')
    print()

    # What expert_mult needed for 850B?
    target = 850000000000
    current_without_moe = embed_params + dense_total + output_params
    needed_moe = target - current_without_moe
    needed_per_expert = needed_moe / n_experts
    needed_expert_mult = needed_per_expert / (2 * d_model * d_ff) - 1

    print(f'Current without MoE: {current_without_moe:,}')
    print(f'Needed MoE contribution: {needed_moe:,}')
    print(f'Needed per expert: {needed_per_expert:,}')
    print(f'Needed expert_mult: {needed_expert_mult:.2f}')

if __name__ == "__main__":
    main()
