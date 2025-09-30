#!/usr/bin/env python3
import json

def main():
    # Load model config
    with open('configs/model/oracle850b.moe.json', 'r') as f:
        config = json.load(f)

    # Calculate parameters
    vocab_size = config['vocab_size']
    d_model = config['dense']['d_model']
    n_layers = config['dense']['n_layers']
    d_ff = config['dense']['d_ff']
    n_experts = config['moe']['experts']
    expert_mult = config['moe']['expert_hidden_mult']

    print('Model Architecture Verification:')
    print(f'Model: {config["model_name"]}')
    print(f'Architecture: {config["arch"]}')
    print(f'Declared parameters: {config["param_total"]:,}')
    print()

    # Dense component
    attn_params = 4 * (d_model * d_model)  # Q,K,V,O projections
    ffn_params = 2 * (d_model * d_ff)      # Two linear layers in FFN
    dense_layer = attn_params + ffn_params
    dense_total = n_layers * dense_layer

    print(f'Dense component: {dense_total:,} parameters')
    print(f'  Attention: {attn_params:,} per layer')
    print(f'  FFN: {ffn_params:,} per layer')

    # MoE component
    expert_dim = int(d_ff * expert_mult)
    expert_ffn = 2 * (d_model * expert_dim)
    moe_total = n_experts * expert_ffn

    print(f'MoE component: {moe_total:,} parameters')
    print(f'  Experts: {n_experts}')
    print(f'  Expert dimension: {expert_dim:,}')
    print(f'  Parameters per expert: {expert_ffn:,}')

    # Embeddings and output
    embeddings = vocab_size * d_model
    output = d_model * vocab_size

    print(f'Embeddings: {embeddings:,} parameters')
    print(f'Output layer: {output:,} parameters')

    # Total calculation
    calculated_total = dense_total + moe_total + embeddings + output
    print(f'Calculated total: {calculated_total:,}')
    print(f'Declared total: {config["param_total"]:,}')
    print(f'Match: {"YES" if calculated_total == config["param_total"] else "NO"}')

    # Active parameters per token
    active_experts = config['moe']['router']['k']
    active_dense = dense_layer
    active_moe = expert_ffn * active_experts
    active_per_token = (active_dense + active_moe) / n_layers

    print(f'Active parameters per token: ~{active_per_token/1e9:.1f}B')

if __name__ == "__main__":
    main()
