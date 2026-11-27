"""Set pooling block of the encoder. The appendix figure has to show exactly this."""
from __future__ import annotations

import torch
from torch import nn


class SetPool(nn.Module):
    """Pools a set of n tokens into K tokens with learned seed queries, conditioned on a vector c."""

    def __init__(self, dim: int = 256, n_seeds: int = 8, heads: int = 4, mlp_ratio: int = 4, cond_dim: int = 64):
        super().__init__()
        self.seeds = nn.Parameter(torch.randn(n_seeds, dim) * 0.02)
        self.norm_q = nn.LayerNorm(dim)     # the seeds (queries)
        self.norm_kv = nn.LayerNorm(dim)    # the set (keys and values)
        self.attn = nn.MultiheadAttention(dim, heads, batch_first=True)
        self.norm_mlp = nn.LayerNorm(dim)
        self.mlp = nn.Sequential(nn.Linear(dim, mlp_ratio * dim), nn.GELU(), nn.Linear(mlp_ratio * dim, dim))
        self.cond_proj = nn.Linear(cond_dim, dim)

    def forward(self, x: torch.Tensor, c: torch.Tensor, pad: torch.Tensor | None = None) -> torch.Tensor:
        # x: (batch, n, dim) the set; c: (batch, cond_dim); pad: (batch, n), True where padded
        q = self.seeds.expand(x.shape[0], -1, -1)
        kv = self.norm_kv(x)
        h = q + self.attn(self.norm_q(q), kv, kv, key_padding_mask=pad, need_weights=False)[0]
        h = h + self.mlp(self.norm_mlp(h))
        return h + self.cond_proj(c).unsqueeze(1)       # (batch, K, dim)
