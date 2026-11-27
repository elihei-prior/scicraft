---
type: llm
focus: output
weight: 1
---

The card draws two separate LayerNorm boxes before the attention, one on the seed (query) stream and one on the set (key and value) stream, as norm_q and norm_kv in pool_block.py
