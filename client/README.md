# client/

Everything that runs on the player's machine: the game client, the auto-updater,
the Flash UI, and the pre-built binaries shipped with the repo.

## Layout

| Path | Contents |
|------|----------|
| `src/pw-game` | C++ sources for `PW_Game.exe` (the main game client) |
| `src/pw-client` | C++ sources for lobby/castle features |
| `src/client` | Shared client glue — overtips, console, command binds |
| `src/pw-mini-launcher` | C++ sources for `PW_MiniLauncher.exe` |
| `build/Bin` | Pre-built executables: `PW_Game.exe`, `PF_Editor.exe`, `PF_EditorC.exe`, `PW_MiniLauncher.exe`, `DBCodeGen.exe`, `CrashSender.exe`, `CubeMapGen.exe`, `DxTex.exe`, `pcnsl.exe` |
| `build/{Data,Localization,Profiles}` | Runtime junctions created by `tools/setup/setup.ps1` |
| `launcher/v1.5` | `PWLauncher.exe` — auto-updater that fetches xdelta patches |
| `flash-ui` | Flash sources (`.fla`), compiled `.swf`, AS3 sources (`src/`, `classes/`), `SwfValidator.exe` |

## Entry points

- **Game:** `client/build/Bin/PW_Game.exe` — see [docs/SETUP.md](../docs/SETUP.md)
- **Editor:** `client/build/Bin/PF_Editor.exe` — see [editor/README.md](../editor/README.md)
- **Launcher:** `client/launcher/v1.5/Launcher/PWLauncher.exe`

## Builds

- C++ sources build with Visual Studio (mix of `.vcproj` / `.vcxproj`).
- Flash `.swf` are built from `.fla` via the Flash IDE; AS3 in `flash-ui/src` is
  Tamarin-targeted.

## Dependencies

- `engine/` — render, scene, sound, network, ui, types, scripts (linked statically).
- `vendor/` — DirectX, FMOD, CEF, Boost, Tamarin, CrashRpt.
- `assets/`, `localization/`, `profiles/` — runtime data, mounted via junctions.

## See also

- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) — overall component map
- [docs/SETUP.md](../docs/SETUP.md) — first-run walkthrough
- [docs/REPO_STRUCTURE.md](../docs/REPO_STRUCTURE.md) §6.2 — runtime data discovery
