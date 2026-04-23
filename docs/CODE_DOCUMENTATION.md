# Prime-World — Code documentation standard

How and where to document code in this repository. The aim is the bare
minimum that lets a future reader (including future you) understand intent
without re-deriving it from the code.

- [Principles](#principles)
- [What gets a comment](#what-gets-a-comment)
- [What does not](#what-does-not)
- [Per-language conventions](#per-language-conventions)
  - [C++](#c)
  - [C#](#c-1)
  - [Python](#python)
  - [PHP](#php)
  - [ActionScript 3](#actionscript-3)
  - [Lua](#lua)
  - [HLSL shaders](#hlsl-shaders)
- [Module-level docs](#module-level-docs)
- [Repo-level docs](#repo-level-docs)
- [API reference generation](#api-reference-generation)
- [Examples](#examples)

## Principles

1. **Default to no comment.** Well-named identifiers describe *what* the
   code does. Add a comment only when the *why* is non-obvious — a hidden
   constraint, a workaround for a specific bug, an invariant that would
   surprise a reader.
2. **Document the boundary, not the body.** Public APIs (header files,
   exported functions, RPC entry points, schema fields) carry doc-comments.
   Private internals carry only the comments that earn their keep.
3. **Comments rot.** Anything that ties a comment to a specific PR, ticket,
   commit hash, or caller will go stale. Keep that context in the PR
   description and `git blame`.
4. **One canonical place per fact.** A subsystem's overview lives in its
   `README.md`; its top-level intent lives in `docs/ARCHITECTURE.md`; an
   API's contract lives next to its declaration. Don't duplicate.
5. **English in committed text.** Conversation and PR descriptions can be
   any language; comments and committed docs in English so all contributors
   can read them.

## What gets a comment

Use a comment when at least one is true:

- The code embodies a workaround for an external bug; cite the bug.
- The code follows a non-obvious invariant the reader can't infer locally
  ("this list is sorted by descending priority because the dispatcher
  iterates back-to-front").
- A constant has a meaning that the value alone does not convey
  ("// 4 frames @ 30 Hz — matches the lock window the relay enforces").
- A control-flow choice is surprising ("we re-enter `Tick` here because
  AdventureScreen does not exist yet at boot").
- A function's contract has an edge case the type system can't capture
  ("returns nullptr if and only if the asset cache is mid-flush").

## What does not

Skip the comment when:

- It restates the code (`// increment counter` over `++counter;`).
- It names the function above its declaration (the function name does
  that already).
- It cites the PR / ticket / author that wrote it (use `git blame`).
- It mentions "used by X" or "called from Y" (greppable; rots fast).
- It is a banner of `=========` or `***` separators.
- It marks future work without an owner or issue link
  (`// TODO: improve this` — either make a ticket or delete).

## Per-language conventions

### C++

- **Header files (.h, .hpp)** — every public class, function, and
  non-trivial member gets a Doxygen-style `///` comment describing its
  contract. Keep it to one or two lines unless an edge case demands more.
- **Implementation files (.cpp, .ipp)** — comment only the non-obvious.
  Do not duplicate the header doc-comment.
- **File header** — top-of-file block only when the file deserves one
  (a self-contained subsystem). Format:
  ```cpp
  // <filename> — one-line subsystem purpose
  ```
  No author, no date, no copyright per file (we have a top-level LICENSE).
- **Namespaces** — at most a one-line comment on namespace open if the
  name is opaque.
- **Macros** — every non-trivial macro gets a doc-comment. Macros are
  invisible in IDEs; comments are the only signal.
- **Doxygen tags** to use: `\brief`, `\param`, `\return`, `\throws`,
  `\note`, `\warning`. Skip `\author`, `\date`, `\since`, `\version`.

### C#

- **Public API** — XML doc-comments (`///`) on classes, methods,
  properties, events. Use `<summary>`, `<param>`, `<returns>`,
  `<exception>`, `<remarks>` for non-obvious notes.
- **Internal helpers** — comment only the non-obvious.
- **Schema files (`engine/types/*.cs`, etc.)** — every type and field gets
  a one-line `<summary>` because these are the schema documentation that
  the editor surfaces in tooltips.

### Python

- **Module docstrings** — every module gets a one-paragraph docstring at
  the top describing its role.
- **Public functions / classes** — Google-style or PEP 257 docstrings
  with `Args:`, `Returns:`, `Raises:`. Internal helpers — only when the
  contract is non-obvious.
- **Type hints** — use them on new code. Don't rewrite legacy
  Python 2-era code just to add hints; do it opportunistically when you
  touch the function.

### PHP

- **PHPDoc** on classes and public methods (`@param`, `@return`,
  `@throws`). Internal methods — only when non-obvious.
- **File header** — `namespace` line and a one-paragraph comment if the
  file is a non-trivial subsystem.

### ActionScript 3

- **ASDoc** on public API of `client/flash-ui/src/**` classes. AS3 is
  end-of-life; treat the docs as defensive — the next reader may not
  speak Flash.

### Lua

- **Top-of-file comment** describing what gameplay system this script
  belongs to (`assets/scripts/Heroes/Foo/Bar.lua` → "talent script for
  Foo's Bar ability"). Inline comments only for non-obvious branches.

### HLSL shaders

- **Top-of-file** — one-paragraph description of pass / pipeline stage,
  inputs, outputs.
- **Constants** — comment any tweakable constants with their valid range.
- **Sampler / texture slots** — comment which slot index they live at;
  the binding is implicit and would otherwise be invisible.

## Module-level docs

Every top-level module has a `README.md` at its root. Required sections:

1. **Purpose** — one sentence.
2. **Layout** — table of subfolders and what each contains.
3. **Entry points / build artefacts** — what this module produces.
4. **Builds with** — toolchain.
5. **Dependencies** — other modules / vendor libs it depends on.
6. **See also** — links to `docs/ARCHITECTURE.md` and any deeper docs.

The existing `client/README.md`, `server/README.md`, `engine/README.md`,
`editor/README.md` follow this template. New top-level folders get one
before merge.

Sub-modules deeper in the tree (e.g. `engine/render/`,
`server/social/coordinator/`) get a `README.md` only when the sub-module
has an interesting overview that doesn't fit in the parent README.

## Repo-level docs

These are the canonical documents and what each is for. Keep this list in
sync with reality.

| Document | Purpose | Audience |
|----------|---------|----------|
| [`README.md`](../README.md) | Project pitch + quick start | Everyone landing on the repo |
| [`LICENSE.md`](../LICENSE.md) | Licence summary | Anyone evaluating use |
| [`docs/REPO_STRUCTURE.md`](REPO_STRUCTURE.md) | Physical layout + migration map | Anyone navigating the tree |
| [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) | Conceptual layout, components, data flow | Contributors writing or reading code |
| [`docs/SETUP.md`](SETUP.md) | First-run walkthrough on a fresh Windows machine | New contributors |
| [`docs/REFACTORING_PLAN.md`](REFACTORING_PLAN.md) | Staged plan for cleaning up structural debt | Contributors picking refactor work |
| [`docs/CODE_REVIEW.md`](CODE_REVIEW.md) | Review process, PR template, ownership | Authors and reviewers |
| [`docs/CODE_DOCUMENTATION.md`](CODE_DOCUMENTATION.md) | This file — how to document code | Anyone writing comments or docs |
| `docs/readme/README.<locale>.md` | Translated top-level READMEs | Locale-specific contributors |
| `docs/legal/` | Licence PDFs | Legal reference |
| `docs/Prime World Art Tech Specs/` | Original art-pipeline specs | Artists |
| `docs/vendor-notes/` | Notes about specific vendored libraries | Engine maintainers |

## API reference generation

We do **not** run a Doxygen / Sphinx site today. If we ever do, the
expected configuration is:

- **Doxygen** for C++ — input `engine/`, `client/src/`, `server/battle/src/`,
  `editor/src/pf-editor-native`. `EXTRACT_ALL = NO`. Generates HTML to
  `dist/docs/cpp/`.
- **DocFX** for C# — input `editor/src/**/*.csproj`,
  `engine/types/**/*.csproj`, `server/control-center/**/*.csproj`.
- **Sphinx** for Python — input `server/social/`. Use the napoleon
  extension for Google-style docstrings.

These are *aspirational*. Until they are wired up, treat the in-source
doc-comments as the reference.

## Examples

### Good — explains the *why* a reader can't infer

```cpp
// Read-back from the device must happen before End-Scene; ATI drivers
// stall the queue otherwise (PW-3142).
device->GetRenderTargetData(rt, dst);
```

### Bad — restates the code

```cpp
// Get the render target data
device->GetRenderTargetData(rt, dst);
```

### Good — captures a non-trivial constant

```cpp
// 4 frames @ 30 Hz — matches the lock window the relay enforces.
constexpr int kInputBufferTicks = 4;
```

### Bad — author / ticket / history

```cpp
// Added by Petya for ticket #4711 in 2012-08-14
constexpr int kInputBufferTicks = 4;
```

### Good — header doc on public API

```cpp
/// Resolves a virtual-filesystem path against the active mount table.
/// \param logical_path  Path using forward slashes, no leading slash.
/// \return Absolute filesystem path; empty string if not found.
/// \note Falls back through case-insensitive lookups to support
///       pre-restructure asset paths until they are migrated.
std::string ResolveAssetPath(std::string_view logical_path);
```

### Bad — duplicates the function name

```cpp
/// Resolves an asset path.
std::string ResolveAssetPath(std::string_view logical_path);
```
