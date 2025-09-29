#!/usr/bin/env python3
"""
Oracle850B MoE Router
Expert routing and load balancing
Author: MagistrTheOne|Краснодар|2025
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, Tuple, Optional
import math


class LoadBalancedRouter(nn.Module):
    """Load-balanced router for MoE"""
    
    def __init__(self, d_model: int, num_experts: int, top_k: int = 2,
                 load_balancing_loss: float = 0.01):
        super().__init__()
        self.d_model = d_model
        self.num_experts = num_experts
        self.top_k = top_k
        self.load_balancing_loss = load_balancing_loss
        
        # Router network
        self.router = nn.Linear(d_model, num_experts, bias=False)
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Forward pass with load balancing"""
        # x: [batch_size, seq_len, d_model]
        logits = self.router(x)  # [batch_size, seq_len, num_experts]
        
        # Top-k selection
        top_k_logits, top_k_indices = torch.topk(logits, self.top_k, dim=-1)
        top_k_probs = F.softmax(top_k_logits, dim=-1)
        
        # Load balancing loss
        router_probs = F.softmax(logits, dim=-1)
        load_balancing_loss = self._compute_load_balancing_loss(router_probs)
        
        return top_k_probs, top_k_indices, load_balancing_loss
    
    def _compute_load_balancing_loss(self, router_probs: torch.Tensor) -> torch.Tensor:
        """Compute load balancing loss"""
        # router_probs: [batch_size, seq_len, num_experts]
        
        # Average probability per expert
        expert_probs = router_probs.mean(dim=(0, 1))  # [num_experts]
        
        # Load balancing loss (encourage uniform distribution)
        load_balancing_loss = self.load_balancing_loss * (
            expert_probs * torch.log(expert_probs + 1e-8)
        ).sum()
        
        return load_balancing_loss


class ExpertCapacityManager:
    """Manage expert capacity and routing"""
    
    def __init__(self, num_experts: int, capacity_factor: float = 1.25):
        self.num_experts = num_experts
        self.capacity_factor = capacity_factor
        
    def compute_capacity(self, seq_len: int) -> int:
        """Compute capacity for experts"""
        return int(self.capacity_factor * seq_len)
    
    def route_tokens(self, router_probs: torch.Tensor, 
                    top_k_indices: torch.Tensor,
                    capacity: int) -> Dict[int, torch.Tensor]:
        """Route tokens to experts with capacity constraints"""
        batch_size, seq_len, _ = router_probs.shape
        
        # Flatten for routing
        flat_probs = router_probs.view(-1, self.num_experts)
        flat_indices = top_k_indices.view(-1, self.top_k)
        
        # Route tokens to experts
        expert_assignments = {}
        
        for expert_idx in range(self.num_experts):
            # Find tokens assigned to this expert
            expert_mask = (flat_indices == expert_idx).any(dim=-1)
            
            if expert_mask.any():
                # Get token indices for this expert
                token_indices = torch.where(expert_mask)[0]
                
                # Apply capacity constraint
                if len(token_indices) > capacity:
                    # Select top tokens by probability
                    expert_probs = flat_probs[token_indices, expert_idx]
                    _, top_tokens = torch.topk(expert_probs, capacity)
                    token_indices = token_indices[top_tokens]
                
                expert_assignments[expert_idx] = token_indices
        
        return expert_assignments


class Oracle850BRouter(nn.Module):
    """Main router for Oracle850B"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        
        # Router parameters
        d_model = config["dense"]["d_model"]
        num_experts = config["moe"]["experts"]
        top_k = config["moe"]["router"]["k"]
        load_balancing_loss = config["moe"]["router"]["load_balancing_loss"]
        
        # Router components
        self.router = LoadBalancedRouter(
            d_model, num_experts, top_k, load_balancing_loss
        )
        self.capacity_manager = ExpertCapacityManager(
            num_experts, config["moe"].get("capacity_factor", 1.25)
        )
        
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Forward pass through router"""
        # Get routing decisions
        probs, indices, load_balancing_loss = self.router(x)
        
        # Compute capacity
        seq_len = x.shape[1]
        capacity = self.capacity_manager.compute_capacity(seq_len)
        
        # Route tokens to experts
        expert_assignments = self.capacity_manager.route_tokens(
            probs, indices, capacity
        )
        
        return probs, indices, load_balancing_loss, expert_assignments


if __name__ == "__main__":
    # Test router
    config = {
        "dense": {"d_model": 6144},
        "moe": {
            "experts": 64,
            "router": {"k": 2, "load_balancing_loss": 0.01},
            "capacity_factor": 1.25
        }
    }
    
    router = Oracle850BRouter(config)
    x = torch.randn(2, 1024, 6144)
    
    probs, indices, loss, assignments = router(x)
    print(f"Router output shapes: {probs.shape}, {indices.shape}")
    print(f"Load balancing loss: {loss.item():.4f}")
    print(f"Expert assignments: {len(assignments)} experts")
