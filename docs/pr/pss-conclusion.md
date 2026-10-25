# L5P 4/4: one-page conclusion, STATUS with all method rows

**Branch**: `pss/conclusion`. It contains main (L5P tools and reference), `pss/method-a` and `pss/methods-bc`, so
merging it brings PR 2 and PR 3 with it.

## What this adds

- `docs/L5P_CONCLUSION.md`: the one-page conclusion, covering the question, the answer table, what was learned,
  what would be worth trying next (each needing a new registration), and the cost.
- `results/L5P/results.csv` and `STATUS.md`, regenerated with all 27 rows: 5/5 bars PASS, and all 14 method rows
  read from `results/L5P/methods/`. `pss/final.py` now reads the method summaries from that folder.
- An L5P row in the README status table, and an "Unreleased" entry in `docs/RELEASE_NOTES.md`.

## The answer, in one table

| method | total cycles | registered result | natural-equivalent cycle of the end state (post hoc) |
|---|---|---|---|
| natural marching | **4195** | reference | - |
| Graves-Morris m = 0 | 640 | FAIL (budget) | 3302 |
| BRR p = 6 | 640 | FAIL (budget) | 2925 |
| Graves-Morris m = 3 | 640 | FAIL (budget) | 2822 |
| BRR p = 3 | 640 | FAIL (budget) | 1112 |
| Newton-Picard p = 2 | 639 | FAIL (budget) | 625 |
| Newton-Picard p = 3 | 639 | FAIL (budget) | 568 |
| Newton-Picard p = 1 | 639 | FAIL (budget) | 391 |

All seven FAIL by the registered rule. The study's main finding is the slow multiplier, 0.99878 rather than 0.9967:
it sets the natural cost at about 4200 cycles and explains why Newton-Picard with a 1-3 dimensional subspace cannot
help.

## Size of the whole study

- **9354 cycles**: PR 1 5157, PR 2 1797, PR 3 2400.
- About 200 rounds in all, most of them monitor events during the long runs. PR 4 itself took about 5 rounds and
  0 cycles.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01VmevXLRq7SmGut51MTYG7i
