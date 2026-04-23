# editor/

PF_Editor — the in-house data editor used to author `.xdb` objects, particle
systems, materials, level layouts, tutorial scripts and balance formulas.

## Layout

| Folder | Purpose | Language |
|--------|---------|----------|
| `src/pf-editor` | Main editor app (WinForms shell) | C# |
| `src/pf-editor-c` | Console-mode build (used by automation / batch jobs) | C# |
| `src/pf-editor-native` | C++ side: rendering / FMOD interop hosted in the editor | C++ |
| `src/editor-lib`, `src/editor-native`, `src/editor-plugins` | Reusable editor libraries and plugins | C# / C++ |
| `src/easel-level-editor` | Level / map editor | C# |
| `src/db-code-gen` | Generates C++/C# accessors from `engine/types/*.cs` schemas | C# |
| `src/formula-builder` | Formula DSL editor (talents, balance) | C# |
| `src/pf-type-icons` | Icons used by the object browser | resources |
| `build/` | Editor config (`config.txt`, `pw_game_lang.ini`) — **the `PF_Editor.exe` binary itself ships in `client/build/Bin/`** because it is co-installed with the client |

## Entry point

`client/build/Bin/PF_Editor.exe` (or `PF_EditorC.exe` for the console build).

## Builds

- MSBuild via per-project `.csproj` / `.vcxproj`.
- `db-code-gen` is run as a build step before the rest of the editor — it
  reads `engine/types/*.cs`, `engine/pf-types/*.cs`, `engine/social-types/*.cs`
  and produces accessor classes used by both editor and the C++ runtime.

## Dependencies

- `engine/types`, `engine/pf-types`, `engine/social-types` — the schema layer.
- `engine/` (native) — for rendering / sound preview inside the editor.
- `vendor/` — wxWidgets (legacy bits), DirectX, FMOD.

## First-run configuration

When you first open `PF_Editor.exe`:
1. `Tools → File System Configuration → Add → WinFileSystem`
2. Set the system root to `assets/` at the repo root.
3. `Views → Object Browser`, `Views → Properties Editor` — these are the
   primary panels.

## See also

- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) §2.4
- Top-level [README.md](../README.md) §"Game Data Editor"
