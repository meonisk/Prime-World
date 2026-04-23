# Prime-World — Refactoring plan

This document is the staged plan for reducing the structural debt in the
codebase that was inherited from the 2026 layout migration and from a decade
of organic growth. It is intentionally **conservative** — Prime World ships
runnable binaries today, and the only acceptable failure mode for a refactor
is "no observable change in behaviour".

- [Principles](#principles)
- [Out of scope](#out-of-scope)
- [Phase 0 — baseline](#phase-0--baseline)
- [Phase 1 — build & path hygiene](#phase-1--build--path-hygiene)
- [Phase 2 — mechanical clean-up](#phase-2--mechanical-clean-up)
- [Phase 3 — semantic clean-up](#phase-3--semantic-clean-up)
- [Phase 4 — modernisation](#phase-4--modernisation)
- [Module-by-module priority](#module-by-module-priority)
- [Definition of done](#definition-of-done)

## Principles

1. **Behaviour-preserving.** Every PR in Phases 0–3 must leave runtime output
   identical. Phase 4 may change observable behaviour but only behind explicit
   compile-time switches.
2. **One change kind per PR.** A PR either renames things, or moves files, or
   reformats, or fixes a bug — never two of those at once. Mixed PRs are
   un-reviewable.
3. **Small enough to revert.** Aim for PRs under ~500 changed lines (excluding
   pure renames). Revert plan: `git revert <sha>` and the build still works.
4. **Tests gate every phase.** Each phase ends with a green build + manual
   smoke test of `PW_Game.exe` (lobby → match → end). No phase merges if the
   smoke test breaks.
5. **Touch what you read.** Every refactor is opportunistic — if you are
   already in a file fixing something, leave it cleaner than you found it.
   Do not schedule isolated "cleanup tickets" that nobody reads.

## Out of scope

The following are **not** part of this plan and require a separate proposal:
- Changing the `.xdb` data format.
- Changing the network protocol between client and battle server.
- Migrating off Flash UI.
- Migrating off DirectX 9.
- Replacing FMOD or Tamarin.
- Anything in `assets/`, `assets-source/`, `localization/`, or `vendor/`.
- Anything in `archive/`.

## Phase 0 — baseline

**Goal:** make the current state buildable and testable so subsequent phases
have a green baseline to compare against.

| Task | Owner module | Notes |
|------|--------------|-------|
| Document how to build `engine/` from CMake on a fresh Windows VM | `engine/` | First check whether `CMakeLists.txt` even succeeds today |
| Document how to open `PF.sln` in current VS and build | `engine/` + `client/` | Capture the exact VS version that works |
| Add a `tools/smoke-test/` script that launches `PW_Game.exe`, waits for the lobby, joins a local match, and exits cleanly | `tools/` | Reusable in CI; first version can be Pythonic UI automation |
| Capture a baseline run log of `PW_Game.exe` boot for diff comparison in later phases | `client/` | Drop into `tools/smoke-test/baseline.log` |
| Get `tools/setup/setup.ps1 -Check` to pass clean from a fresh clone | `tools/setup` | Already mostly works — fix any drift |

**Exit criteria:** smoke-test script exits 0 on a fresh checkout after
`setup.ps1`.

## Phase 1 — build & path hygiene

**Goal:** kill the ghosts of the pre-restructure layout from build files. No
source-code logic changes.

| Task | Owner | Notes |
|------|-------|-------|
| Rewrite `engine/CMakeLists.txt`'s `${SRC_DIR}/../Vendor` to use the new `vendor/` (lower-case) at the right relative depth | `engine/` | Verify each `include_directories(${VENDOR}/...)` resolves |
| Sweep `engine/**/*.vcxproj`, `client/src/**/*.vcxproj`, `server/battle/src/**/*.vcxproj`, `editor/src/**/*.vcxproj` for hard-coded `..\..\..\Src\`, `..\..\Vendor\`, `..\..\Data\` paths and update to new layout | per-module | Phase 3 of the migration did a textual rewrite; verify and finish |
| Audit `*.sln` files for project paths that no longer exist or point through the old layout | per-module | One PR per `.sln` |
| Delete or upgrade `.vcproj` (VS2008 format) files where a sibling `.vcxproj` already exists | mostly `engine/` | Document the VS version lock if any are kept |
| Move the `editor/build/` config files into `client/build/Bin/` next to the `PF_Editor.exe` they configure (or document why they are split) | `editor/` | Decide based on which path the exe reads at runtime |
| Add a top-level `BUILD.md` describing the canonical build commands for each toolchain (CMake, MSBuild, Python, PHP) | `docs/` | Source of truth for CI |
| Pick one of CMake or `PF.sln` as the canonical engine build, document the choice, mark the other as legacy with a deprecation note in its top-of-file | `engine/` | High-impact decision — write a short ADR first |

**Exit criteria:** `engine/` and `client/src/pw-game/` build clean from the
canonical toolchain on a fresh VM, with no warnings about missing paths.

## Phase 2 — mechanical clean-up

**Goal:** apply automated, safe transformations across the C++/C#/Python tree.
All of these are tool-driven; humans only review the diff.

| Task | Tooling | Scope |
|------|---------|-------|
| Apply `clang-format` with a single committed `.clang-format` to all of `engine/`, `client/src/`, `server/battle/src/`, `editor/src/pf-editor-native` | `clang-format` | One PR per top-level folder; nothing else changes |
| Apply `dos2unix` (or its inverse) consistently to source files | `dos2unix` | Decide LF vs CRLF in `.gitattributes` first |
| Trim trailing whitespace, normalise final newlines | editor / pre-commit | Same PRs as `clang-format` |
| Apply `black` + `isort` to all Python under `server/social/`, `server/socagr/` (PHP — `php-cs-fixer`), `tools/**/*.py` | `black`, `isort`, `php-cs-fixer` | Per-tool / per-service PRs |
| Sort `#include` directives within each translation unit | `clang-format` (IncludeCategories) | Bundle with clang-format pass |
| Convert tabs ↔ spaces consistently per `.clang-format` | `clang-format` | Same |
| Delete obviously-dead `#if 0` / `#if FALSE` blocks older than 5 years (check `git blame`) | manual | Per-file PRs; small |
| Delete commented-out code where `git blame` confirms it is older than the last shipping release | manual | Same |

**Exit criteria:** entire C++ tree passes `clang-format --dry-run --Werror`;
Python tree passes `black --check`; CI lints all new commits.

## Phase 3 — semantic clean-up

**Goal:** remove duplication, dead code, and hard-coded path strings without
changing behaviour.

| Task | Module | Notes |
|------|--------|-------|
| Replace literal `"Data/..."`, `"Bin/..."`, `"Tools/..."` path strings in C++ with calls to a single path-resolution function | `engine/system` + clients | Track via `grep -rn '"Data/' engine/ client/`. Do per-subsystem PRs |
| Delete unused C++ classes / functions identified by `cppdepend` or compiler dead-code reports | `engine/`, `client/src/` | Run after Phase 0 has a working build |
| De-duplicate `assets/` ↔ `server/battle/build/Data/` — replace the mirror with a build-time copy step or a single symlink convention | `server/battle/`, `tools/` | Decide based on how the binary opens the path; document in REPO_STRUCTURE.md §6.3 |
| Remove the case-sensitive aliases (`GameLogic`, `MiniGames`, `GFX_Textures`, `Server`, `Dialog`, `SocialTest`) from `tools/setup/setup.ps1` after the path resolver in `engine/system` is taught the new kebab-case names | `engine/system`, `tools/setup` | Big enough to be its own ADR |
| Identify `engine/samples/*` that no longer compile or are unreferenced and move them to `archive/engine-samples/` | `engine/` | Each sample its own PR |
| Audit `archive/` and either restore or delete (no permanent half-archived state) | `archive/` | Per-folder decision |
| Identify duplicated Python utility code across `server/social/` and `server/socagr/` and consolidate into `server/social/libs/` | `server/` | Per-utility PRs |

**Exit criteria:** `git grep '"Data/' engine/ client/ server/` returns zero
hits; `assets/` mirror duplication is gone; smoke test still passes.

## Phase 4 — modernisation

**Goal:** lift the code towards modern toolchains. Every change here is
gated by an ADR (architecture decision record) under `docs/adr/` because each
of these can break things in non-obvious ways.

Candidate work (any of these is its own multi-PR initiative):

- Move C++ to a modern standard (currently looks like C++03 with selective
  C++11). Decide the target (C++14 / C++17), add `/std:c++17` to one project,
  fix what breaks, propagate.
- Replace home-grown smart pointers / containers with `std::` equivalents where
  the semantics match.
- Migrate Python from 2-era idioms (Tornado pre-asyncio, raw `print`-statements)
  to Python 3.
- Replace ad-hoc serialization with a single declarative schema (the
  `engine/types/*.cs` system already gestures this way).
- Replace per-component logging with a single structured logger.
- Move from VS2008/2010-era `.vcproj`/`.vcxproj` to a single CMake-based build.

**Exit criteria:** per-ADR; not a single global gate.

## Module-by-module priority

When picking what to refactor first, follow the rule: **modules that block
other work get prioritised**. Concretely:

| Priority | Module | Reason |
|----------|--------|--------|
| P0 | `engine/CMakeLists.txt`, `engine/PF.sln` | Everything depends on `engine/` building cleanly |
| P0 | `tools/setup/`, `tools/assets/` | Bootstrap path — broken setup blocks all contributors |
| P1 | `client/src/pw-game/`, `client/build/` | Drives the smoke test |
| P1 | `engine/system`, `engine/core` | Path resolution lives here; needed before Phase 3 path work |
| P2 | `server/battle/src/Server/` | Self-contained; has its own consumers |
| P2 | `server/social/` | Python — independent of C++ work; can refactor in parallel |
| P3 | `editor/src/` | Depends on `engine/types` schema stability |
| P3 | `tools/*` (rest) | Each tool is independent; refactor opportunistically |
| P4 | `client/flash-ui/` | Flash is end-of-life; spend time here only on bugs |

## Definition of done

A refactoring task is **done** when:

1. The change is described in the PR body using the [code-review template](CODE_REVIEW.md#pr-template).
2. The build is green on the canonical toolchain (post-Phase 1: CMake or `PF.sln`).
3. The smoke test passes (`tools/smoke-test`).
4. At least one human review approval (see [CODE_REVIEW.md](CODE_REVIEW.md)).
5. If the change touches a public API documented elsewhere, the doc is updated in the same PR.
6. If the change introduces or removes a folder at the top level, [docs/REPO_STRUCTURE.md](REPO_STRUCTURE.md) and [docs/ARCHITECTURE.md](ARCHITECTURE.md) are updated.
