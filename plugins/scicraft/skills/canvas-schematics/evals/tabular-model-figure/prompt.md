---
tags: [skill-creator]
max_turns: 60
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

we need Figure 1 for our neurips submission, deadline is friday. its a self-supervised pretraining scheme for tabular data: we mask ~30% of the cells in each row, a student transformer encodes the masked rows, a predictor predicts the embeddings of the masked cells, and a teacher encoder (EMA of the student) encodes the full rows. loss is between the predicted and the teacher embeddings, no gradient through the teacher. second panel: downstream use, frozen encoder plus a linear probe. the figure should span the full text width, which is 5.5in (139.7mm). our other figures are tikz with dark outlines and pale fills (peach #FBE0C2 model blocks, gray #E8E8EC for the teacher, the loss box in red #D93025), keep it consistent. do this one as a canvas render though, not tikz, our tikz person is away this week. put everything in fig1/ and give me a pdf and a png
