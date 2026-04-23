# Prime-World — Code-review process

This document defines how changes are reviewed. It applies to every pull
request against `main`, regardless of size. The goal is to keep the codebase
in a state where a newcomer can read a PR, understand its intent, and trust
that it does not silently break the game.

- [Principles](#principles)
- [PR template](#pr-template)
- [What the author does](#what-the-author-does)
- [What the reviewer does](#what-the-reviewer-does)
- [Approval criteria](#approval-criteria)
- [When to request changes](#when-to-request-changes)
- [Module ownership](#module-ownership)
- [Tooling: /review and /ultrareview](#tooling-review-and-ultrareview)
- [Edge cases](#edge-cases)

## Principles

1. **Review intent before code.** First read the PR description, then look
   at the diff. If the description does not explain *why*, ask before
   reading.
2. **Small PRs only.** Author splits work so each PR is one change-kind
   (rename, move, reformat, fix, feature) and small enough to review in 15
   minutes. PRs above ~500 changed lines (excluding pure renames) are
   bounced with "please split".
3. **Behaviour-preserving by default.** Every PR claims one of:
   *no behaviour change*, *bug fix*, or *feature*. Reviewer verifies the
   claim — a "refactor" PR that changes a default value is not a refactor.
4. **One reviewer minimum, two for risk.** Risk includes: anything in
   `engine/system`, `engine/core`, `engine/network`; anything that touches
   `.xdb` schemas; anything in `tools/setup`; anything that changes the
   build files.
5. **Reviewers own the merge button.** The author requests review; the
   reviewer merges. This makes the reviewer responsible for "I read this
   and I'm willing to defend it".

## PR template

Every PR description follows this template. Copy it into the PR body when
you open the PR.

```markdown
## What
<one sentence — what the PR does>

## Why
<one or two sentences — what problem this solves, or what it enables>

## Change kind
- [ ] no behaviour change (rename, move, reformat, dead-code removal, comment)
- [ ] bug fix
- [ ] feature
- [ ] build / tooling
- [ ] docs

## How verified
- [ ] `tools/smoke-test` passes
- [ ] manually launched `PW_Game.exe` lobby → match → end
- [ ] new test added (path: …)
- [ ] N/A — docs only

## Risk / blast radius
<which subsystems could break if this is wrong>

## Out of scope
<things the reviewer might expect that this PR intentionally does not do>
```

## What the author does

Before requesting review:

- [ ] Run the canonical build for the touched module.
- [ ] Run `tools/smoke-test` for any change touching `client/`, `engine/` or `assets/` resolution.
- [ ] Self-review the diff one commit at a time — fix what looks weird.
- [ ] Fill in the PR template fully (no "see commits" / "self-explanatory").
- [ ] Tag a reviewer based on [module ownership](#module-ownership).
- [ ] If the PR is mixed-kind ("refactor + bug fix"), split it before requesting review.

## What the reviewer does

Top to bottom:

1. **Read the PR title and template.** If you can't summarise the intent
   in your head after this, stop and ask.
2. **Read the diff.** For each change, ask:
   - Is this the smallest change that accomplishes the stated intent?
   - Does it match the change-kind the author claimed?
   - Does it introduce a path-string, magic constant, or hard-coded
     assumption that should live in config?
   - Could a reader unfamiliar with this PR reconstruct the intent from
     the code alone?
3. **Run the build locally** for risky changes (engine, network, system).
4. **Check the smoke-test artefact** (CI log link) for the correct exit
   code and a clean lobby boot.
5. **Approve or request changes** with specific, actionable comments. Do
   not approve with unaddressed comments.

## Approval criteria

A PR is ready to merge when **all** of:

- Description follows the template.
- Diff matches the stated intent.
- CI is green: build + smoke-test + linters.
- One reviewer (two for risk) has approved without unaddressed comments.
- No `WIP`, `DO NOT MERGE`, `DRAFT` in the title.
- For a behaviour-changing PR, the relevant doc (`README.md`,
  `docs/ARCHITECTURE.md`, etc.) is updated in the same PR.

## When to request changes

Standard reasons:

- **Mixed-kind PR** — split it.
- **Too big** — split it.
- **Missing template fields** — fill them in.
- **Unverified claim** — author says "no behaviour change" but a default value
  shifted; the reviewer makes them prove it (test, log diff, before/after
  screenshot).
- **Hidden coupling** — change touches something the reviewer didn't expect
  given the PR title; ask whether it belongs in this PR.
- **Stale doc** — the PR changes behaviour the docs describe; update the
  doc in the same PR.
- **Dead code or commented-out blocks** — remove or explain.
- **New `TODO` without an owner / issue link** — add or remove.

## Module ownership

Until a `CODEOWNERS` file is in place, use this table to pick reviewers.

| Module | Default reviewer pool |
|--------|------------------------|
| `engine/core`, `engine/system`, `engine/win32`, `engine/memory-lib` | engine maintainers |
| `engine/render`, `engine/scene`, `engine/terrain`, `assets/shaders` | render maintainers |
| `engine/network`, `engine/net`, `server/battle/src/Server/RPC`, `…/NetworkAIO` | network maintainers |
| `engine/sound`, `assets/audio`, `localization/**` | audio / loc maintainers |
| `engine/ui`, `client/flash-ui`, `engine/scripts` (Tamarin bridge) | UI maintainers |
| `engine/game/PF`, `engine/game/PW`, `engine/pf-game-logic`, `engine/pf-minigames` | gameplay maintainers |
| `engine/types`, `engine/pf-types`, `engine/social-types`, `editor/src/db-code-gen` | types / data-format maintainers |
| `client/src/**`, `client/build/**` | client maintainers |
| `client/launcher/**` | launcher maintainers |
| `server/battle/**` | battle-server maintainers |
| `server/social/**` | social maintainers (Python) |
| `server/socagr/**` | aggregator maintainers (PHP) |
| `server/control-center/**` | ops maintainers (.NET) |
| `editor/**` | editor maintainers |
| `tools/setup`, `tools/assets`, `docs/SETUP.md`, top-level `README.md` | onboarding maintainers |
| Other `tools/**` | tool author or last `git log` author |
| `vendor/**` | requires *two* reviewers — vendor changes are LFS-heavy and rare |
| `assets/**`, `assets-source/**` | data maintainers |
| `docs/**` | any maintainer; bias to author of the area being documented |

When in doubt, `git log -- <path>` and tag the most recent non-bot author.

## Tooling: /review and /ultrareview

Two Claude Code skills accelerate review.

- `/review` — single-pass review of the current branch's pending changes,
  using the criteria above. Good for self-review before requesting human
  review.
- `/ultrareview` — multi-agent cloud review of the current branch (or a
  specific GitHub PR via `/ultrareview <PR#>`). User-triggered, billed.
  Good for high-risk changes (build files, schema, network code) where you
  want a second mechanical opinion before a human picks it up.

Neither replaces a human reviewer. They flag issues; a human still owns the
merge.

## Edge cases

- **Vendored binary update.** Two reviewers required. PR must include the
  upstream version, the source URL or commit, and a note on why the update
  is needed.
- **Schema change in `engine/types/`.** Schema changes ripple into both the
  C++ runtime and the editor via `db-code-gen`. PR must include both sides
  of the regenerated code, and a one-line "data migration" plan.
- **Pre-restructure path mention.** Anything that introduces or restores a
  `pw/branches/r1117/...` path is a request-changes — that layout is
  archived.
- **`archive/`.** Changes to `archive/` are documentation-only (a README
  describing what was archived and why). Code changes to archived modules
  are never merged.
- **`vendor/CEF/libcef.dll` and other LFS-tracked binaries.** Bumping these
  requires the LFS quota to be available — see [docs/SETUP.md](SETUP.md).
  PR must explicitly say "LFS budget verified".
