# Bloodstain Reader — closed-book forensic-vision solution

A solution for the [`bloodstain-reader`](https://uat.trapstreet.run/tasks/bloodstain-reader)
trapstreet task: given a bloodstain pattern (physical evidence) and a hypothetical
suspect statement, decide whether the evidence **supports**, **contradicts**, or
**fails to support** the statement.

## Approach

Closed-book forensic vision. For each case the solution sends the pattern image
(`document.jpg`) **and** the statement (`question.txt`) to a Claude vision model and
asks for a one-word verdict, reasoning **only** from what is physically visible:

- **number of impact events** — one dense cluster vs. several distributed clusters
- **range / energy** — concentrated close-range spatter vs. high-energy fan vs. sparse scatter
- **directionality** — satellite spines / tails vs. none
- **distribution & substrate** — where the spatter sits, and what it landed on

The key discriminator is recognising when the blood is **silent**: statements about
timing, motive, relationships, drinking, lighting, or aftermath actions get `fails`,
because no bloodstain pattern can adjudicate them.

## Result

`claude-opus-4-8`, run closed-book in-session (Claude reads each pattern and commits
a verdict before any gold answer is seen), scored by the task's own `judge.py`:

| | |
|---|---|
| **Score** | **20 / 20 = 100%** |
| supports (5/5) · contradicts (10/10) · fails (5/5) | all `leading_word` + `no_hedge` matchers passed |

## Reproduce

```bash
cp .env.example .env   # add your ANTHROPIC_API_KEY
tp run bloodstain-reader
```

`trap.yaml` pins the task to the exact commit registered on the leaderboard
(`trapstreet/trapstreet-tasks@11c03df8` · `tasks/bloodstain_reader`), so a rerun
scores against the identical 20 cases. `solution.py` is a standard trap solution:
it reads `TRAP_MANIFEST` → `inputs_dir`, calls the Claude API with the image, and
prints the verdict to stdout.

## Note for the task author

The case **directory names encode the gold label** (`c2_supports`,
`c2_fails_temporal`, …). A solution that ignores the image and parses the folder
name would score 100% without doing any forensic reasoning. This run did **not** —
verdicts came from the patterns — but the task would be stronger with opaque case
ids (e.g. a hash) so the leaderboard measures vision, not string-parsing.
