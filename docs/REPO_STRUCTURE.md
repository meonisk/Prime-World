# Prime-World Repository Structure

This document describes the repository layout after the 2026 restructure, the
asset inventory on which it is based, and the migration plan that was executed.

- [1. Summary](#1-summary)
- [2. Asset & file inventory](#2-asset--file-inventory)
- [3. Top-level layout](#3-top-level-layout)
- [4. Migration map (old → new)](#4-migration-map-old--new)
- [5. Migration phases](#5-migration-phases)
- [6. Known follow-ups](#6-known-follow-ups)

## 1. Summary

The repository used to mirror the original SVN layout of the game
(`pw/branches/r1117/...`) and spread related things across unrelated top-level
folders (`FlashUI/`, `pw_art/`, `pw_publish/`). The restructure regroups
everything around **domain concepts** — client, server, engine, editor, tools,
assets, source-art, localisation and third-party code.

Goals:

1. A newcomer can tell, from the root folder, what the project contains.
2. Client and server code, binaries and data are visibly separated.
3. Runtime game data (`assets/`) is separated from pre-compiled source art
   (`assets-source/`).
4. Third-party libraries live in their own `vendor/` tree.
5. The legacy SVN path `pw/branches/r1117/` is gone.

## 2. Asset & file inventory

Counts and sizes from the pre-restructure scan of 206 878 non-git files
(~15 GB on disk, LFS-tracked).

### 2.1 Game-engine data

| Kind | Extensions | Files | Size | Source of truth |
|------|------------|-------|------|-----------------|
| Nival data objects | `.xdb` | 50 397 | 483 MB | `assets/` (mirror on `server/battle/build/PvX/Data`) |
| Road meshes | `.road` | 2 480 | — | `assets/maps`, `assets/terrain` |
| Static geometry | `.stat` + `.mayastat` | 9 041 | ~330 MB | `assets/` |

### 2.2 Textures

| Kind | Extensions | Files | Size | Source of truth |
|------|------------|-------|------|-----------------|
| Runtime textures | `.dds` | 8 021 | **1.6 GB** | `assets/ui/Styles`, `assets/gfx-textures`, `assets/heroes/*` |
| Source art | `.png` | 5 632 | 358 MB | `assets-source/` (paired by name with runtime `.dds`) |
| Misc source art | `.tga`, `.psd`, `.bmp` | ~490 | 30 MB | `assets-source/`, `editor/src/**/Resources` |

Pairing convention: `assets-source/styles/Icons/Talents/Abraziv_001.png` →
compiled to → `assets/ui/Styles/Icons/Talents/Abraziv_001.dds`.

### 2.3 Animations, skeletons and skins

| Kind | Extensions | Files | Size |
|------|------------|-------|------|
| Animations | `.anim` + `.mayaanim` | 14 921 | 1.3 GB |
| Skinned meshes | `.skin` + `.mayaskin` | 1 602 | 1.0 GB |
| Skeletons | `.skel` + `.mayaskel` | 1 509 | 3.3 MB |
| Particles | `.part` + `.mayapart` | 9 117 | 245 MB |

Located under `assets/heroes`, `assets/creeps`, `assets/summons`,
`assets/buildings`, `assets/effects`, `assets/pets`, `assets/critters`.

### 2.4 Audio & video

| Kind | Extensions | Files | Size | Location |
|------|------------|-------|------|----------|
| Voice-over | `.wav` | 964 | 328 MB | `localization/{en-US,ru-RU,de-DE,fr-FR,tr-TR,lt-LT,pl-PL,vi-VN,ru-MO}` |
| Sound banks | `.fsb` | — | ~80 MB | `assets/audio` (FMOD banks) |
| Cinematics | `.ogv` | 373 | 625 MB | `assets/` |

### 2.5 Shaders & code

| Kind | Extensions | Files | Primary location |
|------|------------|-------|------------------|
| Shader source | `.hlsl` | 72 | `engine/render/Shaders`, `engine/render/OnlineShaders` |
| Runtime shaders | `.hlsl` (compiled path) | — | `assets/shaders` |
| C++ | `.cpp`, `.h`, `.hpp`, `.ipp` | 30 577 | `engine/`, `client/src`, `server/battle/src`, `editor/src`, `tools/*` |
| C# | `.cs` | 2 489 | `editor/src`, `tools/*` |
| ActionScript | `.as` | 3 404 | `client/flash-ui/`, `engine/` |
| Flash | `.fla`, `.swf` | 133 | `client/flash-ui/`, `assets-source/styles/Icons` |
| Python | `.py` | 3 072 | `server/social`, `tools/*` |
| PHP | `.php` | 1 947 | `server/socagr` |
| Lua | `.lua` | 86 | `engine/scripts`, `assets/scripts` |

### 2.6 Third-party libraries (`vendor/`, ~2 GB)

Boost (361 MB), DirectSSN (219 MB), FMOD (214 MB), Maya (187 MB),
wxWidgets (155 MB), Steam (92 MB), CEF (88 MB), ACE_wrappers (71 MB),
xulrunner-sdk (67 MB), Tamarin (53 MB), MySQL (47 MB), Thrift (36 MB),
MacOS (33 MB), OpenSSL (24 MB), SharpSvn (23 MB), DirectX (23 MB),
CrashRpt (23 MB), libcurl (21 MB), ircdotnet (14 MB), Terabit (9 MB),
and smaller ones.

## 3. Top-level layout

```
/
├── README.md                    Main README (English)
├── LICENSE.md                   Game licence summary
├── .gitattributes / .gitignore
│
├── docs/                        Documentation
│   ├── REPO_STRUCTURE.md        This file
│   ├── readme/                  Translated READMEs (RU, CN, JP, DE, ES, FR, PT, HI, ID)
│   ├── legal/                   LICENSING AGREEMENT *.pdf
│   ├── specs/                   Art Tech Specs, internal configuration PDFs
│   └── PW_trailer.png
│
├── client/                      Everything client-side
│   ├── src/                     C++ sources for client executables
│   ├── build/                   Pre-built PvP client (Bin/, Data/, Localization/, Profiles/)
│   ├── launcher/                LauncherX (auto-updater)
│   └── flash-ui/                Flash UI sources (.fla, .as) and builds (.swf)
│
├── server/                      Everything server-side
│   ├── battle/                  PvX battle server (C++)
│   │   ├── src/                 Source (moved from Src/Server)
│   │   └── build/               Pre-built PvX package
│   ├── social/                  Social backend (Python)
│   ├── socagr/                  Social aggregator (PHP)
│   └── control-center/          Cluster management
│
├── engine/                      Shared C++ game engine (client + server)
│   ├── core/                    Base primitives (Src/Core, Src/PF_Core)
│   ├── render/                  Rendering + HLSL sources
│   ├── scene/                   Scene graph
│   ├── sound/                   Sound subsystem
│   ├── network/                 Net + Network
│   ├── ui/                      UI runtime
│   ├── terrain/                 Terrain
│   ├── system/                  Low-level system glue
│   ├── game-logic/              Game, PF_GameLogic, PF_Minigames
│   ├── types/                   Types, PF_Types*, SocialTypes*
│   ├── scripts/                 Scripting runtime + Lua
│   └── win32/                   Win32 specifics
│
├── editor/                      In-house editor (PF_Editor)
│   ├── src/                     PF_Editor*, EditorLib, EditorNative, EditorPlugins, ...
│   └── build/                   PF_Editor.exe + config
│
├── tools/                       Developer-only utilities
│   ├── censor/ test-framework/ inno-test/ gm-tools/ billing/ install/
│   ├── c-compiler/ fix-sln/ swf-checker/ maya-plugins/ log-analyzer/
│   ├── mesh-converter/ shader-compiler/ debug-var-stat-view/ ...
│
├── assets/                      Runtime game data (what the engine loads)
│   ├── heroes/ creeps/ critters/ buildings/ items/ summons/ pets/
│   ├── maps/ terrain/ effects/ ui/ gfx-textures/ audio/ shaders/
│   ├── faces/ glyphs/ dialogs/ mini-games/ impulses/ game-logic/
│   ├── social/ scripts/ debug/ tech/ server-data/ test/
│
├── assets-source/               Pre-compiled source art
│   ├── styles/ icons/ screens/ cursors/ textures-default/
│
├── localization/                Per-locale voice-over + strings
│   └── en-US/ ru-RU/ de-DE/ fr-FR/ tr-TR/ lt-LT/ pl-PL/ vi-VN/ ru-MO/
│
├── profiles/                    Game config (game.cfg, private.cfg_example)
├── vendor/                      Third-party libraries
└── archive/                     Legacy / deprecated content kept for reference
```

## 4. Migration map (old → new)

| Old path | New path |
|----------|----------|
| `pw/branches/r1117/Src/{Client, PW_Client, PW_Game, PW_MiniLauncher}` | `client/src/` |
| `pw/branches/r1117/Src/Server` | `server/battle/src/` |
| `pw/branches/r1117/Src/{Core, PF_Core}` | `engine/core/` |
| `pw/branches/r1117/Src/Render` | `engine/render/` |
| `pw/branches/r1117/Src/Scene` | `engine/scene/` |
| `pw/branches/r1117/Src/Sound` | `engine/sound/` |
| `pw/branches/r1117/Src/{Net, Network}` | `engine/network/` |
| `pw/branches/r1117/Src/UI` | `engine/ui/` |
| `pw/branches/r1117/Src/Terrain` | `engine/terrain/` |
| `pw/branches/r1117/Src/System` | `engine/system/` |
| `pw/branches/r1117/Src/{Game, PF_GameLogic, PF_Minigames}` | `engine/game-logic/` |
| `pw/branches/r1117/Src/{Types*, PF_Types*, SocialTypes*}` | `engine/types/` |
| `pw/branches/r1117/Src/Scripts` | `engine/scripts/` |
| `pw/branches/r1117/Src/Win32` | `engine/win32/` |
| `pw/branches/r1117/Src/{PF_Editor*, Editor*, EaselLevelEditor, FormulaBuilder}` | `editor/src/` |
| `pw/branches/r1117/Src/{MeshConverter, ShaderCompiler, DBCodeGen, MemoryLib, NivalInput, Samples}` | `tools/*/` |
| `pw/branches/r1117/Src/{Server.Old, PF_ServerCmds.Old}` | `archive/` |
| `pw/branches/r1117/Data/*` | `assets/*/` |
| `pw/branches/r1117/Data/deprecated_shaders` | `archive/deprecated_shaders/` |
| `pw/branches/r1117/Vendor/*` | `vendor/*/` |
| `pw/branches/r1117/Localization/` | `localization/` |
| `pw/branches/r1117/Profiles/` | `profiles/` |
| `pw/branches/r1117/Bin/` | `editor/build/` |
| `pw/branches/r1117/Tools/*` | `tools/*/` |
| `pw/branches/r1117/logs/` | (gitignored, not moved) |
| `pw_art/*` | `assets-source/*/` |
| `pw_publish/branch/Client/PvP/` | `client/build/` |
| `pw_publish/branch/Server/PvX/` | `server/battle/build/` |
| `pw_publish/branch/Server/Social/` | `server/social/` |
| `pw_publish/branch/Server/Socagr/` | `server/socagr/` |
| `pw_publish/branch/Server/ControlCenter/` | `server/control-center/` |
| `pw_publish/LauncherX/` | `client/launcher/` |
| `FlashUI/` | `client/flash-ui/` |
| `README_*.md` (root) | `docs/readme/` |
| `LICENSING AGREEMENT *.pdf` (root) | `docs/legal/` |
| `PW_trailer.png` (root) | `docs/` |

## 5. Migration phases

The restructure was done in ordered phases, each a separate commit, to keep
review manageable and make partial rollback possible.

| Phase | Content | Risk |
|-------|---------|------|
| 0 | This document | none |
| 1 | Root cosmetic cleanup (READMEs, licences, trailer → `docs/`) | none |
| 2 | Top-level folder moves: `FlashUI/`, `pw_art/`, `pw_publish/**` | low (no build deps) |
| 3 | `pw/branches/r1117/Src/` decomposed into `engine/` + `client/src/` + `server/battle/src/` + `editor/src/` + `tools/*/` | **high** — requires updates to `.sln`, `.vcxproj`, `CMakeLists.txt` |
| 4 | `Data/` → `assets/`, `Vendor/` → `vendor/`, `Localization/`, `Profiles/`, `Bin/`, `Tools/` | **high** — game runtime resolves `Data/` paths internally |
| 5 | Archive legacy; update `README.md`; `.gitignore`/`.gitattributes` | low |

## 6. Known follow-ups

Things that were **not** automatically fixed and require human attention after
the restructure:

1. **Build system paths.** `PF.sln`, `SocialTypes_12.sln` and every
   `*.vcxproj` under `engine/`, `client/src`, `server/battle/src`,
   `editor/src` and `tools/*` contain relative paths. Phase 3 does a
   best-effort textual rewrite, but the build must still be verified on a
   Windows machine with Visual Studio.

2. **Runtime data discovery.** `PW_Game.exe` and `PF_Editor.exe` look for
   `Data/`, `Localization/`, `Profiles/` relative to their working directory.
   After Phase 4 these are `assets/`, `localization/`, `profiles/`. Either
   (a) configure the executables via `Profiles/game.cfg` / editor
   `File System Configuration`, or (b) create Windows junctions
   `Data → assets`, `Localization → localization`, `Profiles → profiles`
   in the working directory.

3. **PvX server data duplication.** Before the restructure the PvX server
   shipped its own copy of the game data (25 180 `.xdb` files identical to
   `Data/`). After Phase 4 these sit in
   `server/battle/build/PvX/Data`. Consider deduplicating via a symlink or a
   build-time copy step.

4. **Hard-coded strings in C++.** A number of source files contain literal
   `"Data/..."`, `"Bin/..."`, `"Tools/..."` path strings. These are **not**
   automatically rewritten; they resolve at runtime via the engine's virtual
   filesystem and can be addressed incrementally.

5. **`.gitattributes` LFS rules.** Paths in `.gitattributes` refer to the old
   `pw/branches/r1117/...` prefix. Phase 5 rewrites them to the new layout.
