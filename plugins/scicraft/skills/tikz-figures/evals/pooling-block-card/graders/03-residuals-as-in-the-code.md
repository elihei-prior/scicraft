---
type: llm
focus: output
weight: 1
---

The first residual starts on the seed stream before its LayerNorm and joins after the attention; the MLP has its own LayerNorm before it and its own residual around it
