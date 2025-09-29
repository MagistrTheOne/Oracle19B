#!/usr/bin/env python3
"""
Oracle850B MoE Transformer
Mixture of Experts Transformer with 64 experts, top-k=2 routing
Author: MagistrTheOne|Краснодар|2025
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, Optional, Tuple
import math


class MoERouter(nn.Module):
    """Router for MoE expert selection"""
    
    def __init__(self, d_model: int, num_experts: int, top_k: int = 2):
        super().__init__()
        self.d_model = d_model
        self.num_experts = num_experts
        self.top_k = top_k
        
        # Router network
        self.router = nn.Linear(d_model, num_experts, bias=False)
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass through router"""
        # x: [batch_size, seq_len, d_model]
        logits = self.router(x)  # [batch_size, seq_len, num_experts]
        
        # Top-k selection
        top_k_logits, top_k_indices = torch.topk(logits, self.top_k, dim=-1)
        top_k_probs = F.softmax(top_k_logits, dim=-1)
        
        return top_k_probs, top_k_indices


class MoEExpert(nn.Module):
    """Individual expert network"""
    
    def __init__(self, d_model: int, d_ff: int, activation: str = "swiglu"):
        super().__init__()
        self.d_model = d_model
        self.d_ff = d_ff
        self.activation = activation
        
        # Expert layers
        self.w1 = nn.Linear(d_model, d_ff, bias=False)
        self.w2 = nn.Linear(d_ff, d_model, bias=False)
        self.w3 = nn.Linear(d_model, d_ff, bias=False)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through expert"""
        if self.activation == "swiglu":
            return self.w2(F.silu(self.w1(x)) * self.w3(x))
        else:
            return self.w2(F.relu(self.w1(x)))


class MoELayer(nn.Module):
    """MoE layer with multiple experts"""
    
    def __init__(self, d_model: int, num_experts: int, d_ff: int, 
                 top_k: int = 2, capacity_factor: float = 1.25):
        super().__init__()
        self.d_model = d_model
        self.num_experts = num_experts
        self.top_k = top_k
        self.capacity_factor = capacity_factor
        
        # Router
        self.router = MoERouter(d_model, num_experts, top_k)
        
        # Experts
        self.experts = nn.ModuleList([
            MoEExpert(d_model, d_ff) for _ in range(num_experts)
        ])
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through MoE layer"""
        batch_size, seq_len, d_model = x.shape
        
        # Get routing decisions
        probs, indices = self.router(x)  # [batch_size, seq_len, top_k]
        
        # Calculate capacity
        capacity = int(self.capacity_factor * seq_len)
        
        # Initialize output
        output = torch.zeros_like(x)
        
        # Process each expert
        for expert_idx in range(self.num_experts):
            # Find tokens assigned to this expert
            expert_mask = (indices == expert_idx).any(dim=-1)  # [batch_size, seq_len]
            
            if expert_mask.any():
                # Get tokens for this expert
                expert_tokens = x[expert_mask]  # [num_tokens, d_model]
                
                # Apply expert
                expert_output = self.experts[expert_idx](expert_tokens)
                
                # Get routing weights for this expert
                expert_probs = probs[expert_mask]  # [num_tokens, top_k]
                expert_weights = expert_probs[:, (indices[expert_mask] == expert_idx).nonzero(as_tuple=True)[1]]
                
                # Weighted output
                weighted_output = expert_output * expert_weights.unsqueeze(-1)
                
                # Scatter back to output
                output[expert_mask] += weighted_output
        
        return output


class Oracle850BTransformer(nn.Module):
    """Oracle850B MoE Transformer Model"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        
        # Model parameters
        self.d_model = config["dense"]["d_model"]
        self.n_layers = config["dense"]["n_layers"]
        self.n_heads = config["dense"]["n_heads"]
        self.d_ff = config["dense"]["d_ff"]
        self.vocab_size = config["vocab_size"]
        self.max_seq_len = config["max_seq_len"]
        
        # MoE parameters
        self.num_experts = config["moe"]["experts"]
        self.top_k = config["moe"]["router"]["k"]
        
        # Embeddings
        self.token_embedding = nn.Embedding(self.vocab_size, self.d_model)
        self.position_embedding = nn.Embedding(self.max_seq_len, self.d_model)
        
        # Transformer layers
        self.layers = nn.ModuleList([
            Oracle850BLayer(config) for _ in range(self.n_layers)
        ])
        
        # Output
        self.ln_f = nn.LayerNorm(self.d_model, eps=config.get("rmsnorm_eps", 1e-5))
        self.lm_head = nn.Linear(self.d_model, self.vocab_size, bias=False)
        
    def forward(self, input_ids: torch.Tensor, 
                attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass"""
        batch_size, seq_len = input_ids.shape
        
        # Embeddings
        token_emb = self.token_embedding(input_ids)
        pos_ids = torch.arange(seq_len, device=input_ids.device)
        pos_emb = self.position_embedding(pos_ids)
        
        x = token_emb + pos_emb
        
        # Transformer layers
        for layer in self.layers:
            x = layer(x, attention_mask)
        
        # Output
        x = self.ln_f(x)
        logits = self.lm_head(x)
        
        return logits


class Oracle850BLayer(nn.Module):
    """Single transformer layer with MoE"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.d_model = config["dense"]["d_model"]
        self.n_heads = config["dense"]["n_heads"]
        self.d_ff = config["dense"]["d_ff"]
        self.num_experts = config["moe"]["experts"]
        self.top_k = config["moe"]["router"]["k"]
        
        # Self-attention
        self.attention = nn.MultiheadAttention(
            self.d_model, self.n_heads, batch_first=True
        )
        
        # MoE FFN
        self.moe = MoELayer(
            self.d_model, self.num_experts, self.d_ff, self.top_k
        )
        
        # Layer norms
        self.ln1 = nn.LayerNorm(self.d_model, eps=config.get("rmsnorm_eps", 1e-5))
        self.ln2 = nn.LayerNorm(self.d_model, eps=config.get("rmsnorm_eps", 1e-5))
        
    def forward(self, x: torch.Tensor, 
                attention_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Forward pass through layer"""
        # Self-attention
        attn_out, _ = self.attention(x, x, x, attn_mask=attention_mask)
        x = x + attn_out
        x = self.ln1(x)
        
        # MoE FFN
        moe_out = self.moe(x)
        x = x + moe_out
        x = self.ln2(x)
        
        return x


def create_oracle850b_model(config_path: str) -> Oracle850BTransformer:
    """Create Oracle850B model from config"""
    import json
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    return Oracle850BTransformer(config)


if __name__ == "__main__":
    # Test model creation
    model = create_oracle850b_model("src/oracle/moe850b/configs/model/oracle850b.moe.json")
    print(f"Model created with {sum(p.numel() for p in model.parameters()):,} parameters")
