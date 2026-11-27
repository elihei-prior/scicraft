---
tags: [skill-creator]
max_turns: 60
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

fig 1 for our neurips submission, a JEPA on 2D point clouds (lidar slices). context encoder sees a crop of the scan with some square blocks masked out, target encoder is an EMA of the context encoder and sees the whole crop, the predictor gets the context tokens plus the position of one masked block and predicts the target encoder's embedding of that block, loss is smooth L1 in latent space, stop-grad on the target branch. it sits in the left half of a two-panel figure, so about half the text width (5.5in text). the last version a student made had three losses, a legend and looked like a slide. tex + pdf in fig1/, deadline friday
