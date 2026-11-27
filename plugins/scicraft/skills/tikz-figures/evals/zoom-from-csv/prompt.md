---
tags: [skill-creator]
max_turns: 60
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

attached scan.csv is a 2D slice of one of our lidar scans (x, y in meters, label = class). for the method figure I want the zoom: the whole slice as a density, then nested crops down to the single points, and at the end the kNN graph we build on the points (k = 6). it has to be the real points, not a drawing, and it must rebuild the same every time. TikZ, standalone, put it in zoom_fig/. it will be printed at full text width (5.5in). also tell me the numbers I should put in the caption (points per class, k, window sizes)

Input files: scan.csv
