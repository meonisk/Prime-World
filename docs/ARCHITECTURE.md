# Prime-World — Architecture overview

This document is a map of the codebase: what the top-level folders are, what
each one builds into, and how they are wired together at runtime. It is a
*conceptual* companion to [REPO_STRUCTURE.md](REPO_STRUCTURE.md), which is the
*physical* layout / migration map.

- [1. Bird's-eye view](#1-birds-eye-view)
- [2. Components](#2-components)
  - [2.1 client/](#21-client)
  - [2.2 server/](#22-server)
  - [2.3 engine/](#23-engine)
  - [2.4 editor/](#24-editor)
  - [2.5 tools/](#25-tools)
  - [2.6 assets/, assets-source/, localization/, profiles/](#26-data-folders)
  - [2.7 vendor/](#27-vendor)
- [3. Build artefacts](#3-build-artefacts)
- [4. Runtime data flow](#4-runtime-data-flow)
- [5. Inter-module dependencies](#5-inter-module-dependencies)
- [6. Known structural debts](#6-known-structural-debts)

## 1. Bird's-eye view

Prime World is a 5v5 MOBA shipped in 2014 by Nival on an in-house engine. The
public release covers the *Battle* part (the lobby + match) and the supporting
backend. The repo splits along three axes:

- **What runs where** — `client/`, `server/`, `editor/`, `tools/` are
  endpoints; `engine/` is the shared C++ library all native endpoints link
  against; `vendor/` is third-party.
- **Code vs data** — `assets/` and `localization/` are runtime data the
  binaries load; `assets-source/` is editable source art that compiles into
  `assets/`; `profiles/` is runtime configuration.
- **Source vs build output** — every endpoint has both `src/` (sources) and
  `build/` (pre-compiled binaries shipped in the repo). The build trees are
  what you actually launch; the source trees are what you would rebuild from
  if you change C++.

```
            +--------------------------------------------------+
            |                      assets/                     |
            |    (.xdb game data, .dds textures, .fsb audio,   |
            |          .anim/.skin/.skel, shaders, lua)        |
            +-----------------+----------------+---------------+
                              |                |
                       loads  |                | mirrored into
                              v                v
   +------------+      +-------------+   +----------------+      +-----------+
   |  Flash UI  |<---->| PW_Game.exe |   | Battle server  |<---->|  Social   |
   | (.swf/.as) |      |   (client)  |<->| (UniServerApp) |      | backend   |
   +------------+      +------+------+   +----------------+      | (Python)  |
                              |                                  +-----------+
                              |  edits same .xdb              ^         ^
                              v                               |         |
                      +---------------+                       |         |
                      | PF_Editor.exe |                       |         |
                      +---------------+                       |         |
                                                              |         |
                                          +---------+         |         |
                                          | socagr  |---------+         |
                                          |  (PHP)  |-------------------+
                                          +---------+
                                          aggregator / billing / GM tools
```

## 2. Components

### 2.1 `client/`

The end-user game.

| Sub-tree | Purpose | Language |
|----------|---------|----------|
| `client/src/pw-game` | Main game executable sources | C++ |
| `client/src/pw-client` | Lobby / castle client sources | C++ |
| `client/src/client` | Shared client glue (overtips, console, command binds) | C++ |
| `client/src/pw-mini-launcher` | Lightweight launcher used to bootstrap the main exe | C++ |
| `client/build/Bin` | Pre-built executables: `PW_Game.exe`, `PF_Editor.exe`, `PF_EditorC.exe`, `PW_MiniLauncher.exe`, `DBCodeGen.exe`, `CrashSender.exe`, `CubeMapGen.exe`, `DxTex.exe`, `pcnsl.exe` | — |
| `client/build/{Data,Localization,Profiles}` | Runtime junctions — see [setup](SETUP.md) | — |
| `client/launcher/v1.5` | Auto-updating launcher (`PWLauncher.exe`) — fetches xdelta patches | C++ |
| `client/flash-ui` | Flash-based UI: `.fla` sources, compiled `.swf`, Tamarin-side AS3 in `src/`, `classes/`, plus `SwfValidator.exe` | ActionScript 3 |

**Entry point:** `client/build/Bin/PW_Game.exe`
**Builds with:** Visual Studio (`.vcproj` / `.vcxproj`), Flash IDE / swfmill for `.swf`.

### 2.2 `server/`

Four independent backends. They were originally separate repos; here they
live side by side under one `server/` umbrella.

| Sub-tree | Purpose | Language | Process model |
|----------|---------|----------|---------------|
| `server/battle` | The PvX battle simulation — runs match logic, broadcasts state | C++ | Multiple `UniServerApp-*.cmd` roles (coordinator, lobby, gateway, gamesvc, gamebalancer, chat, livemm, relay, monitoring, clusteradmin, clientctrl, login, …) |
| `server/social` | Social backend: profiles, friends, parties, guilds, chat, sieges, billing, matchmaking | Python (Tornado) | `pwserver.py`, `bro.py`, `coordinator.py`, plus dozens of `*_service.py` daemons |
| `server/socagr` | Aggregator + admin web (billing, GM tooling, web frontend) | PHP (Zend-style) | `application/background/startWorkers.php` + `application/frontend` |
| `server/control-center` | Cluster management UI / orchestration | C# | `ClusterManagement/` |

`server/battle/src/Server/` is the C++ source; `server/battle/build/` is the
pre-built deliverable, with 20+ `*.cmd` scripts in `Bin/` — each launches one
role of the cluster.

`server/battle/build/Data` is a 25 k-file mirror of `assets/` so the battle
server can resolve the same game-data paths as the client. See
[REPO_STRUCTURE.md §6.3](REPO_STRUCTURE.md#6-known-follow-ups) — deduplicating
this is open work.

### 2.3 `engine/`

The shared C++ engine — most of the C++ in the repo lives here. Linked into
`PW_Game.exe`, the battle server, the editor, and several tools.

| Sub-tree | Purpose |
|----------|---------|
| `core/`, `pf-core/` | Base primitives — strings, containers, smart pointers, file IO, threading |
| `system/`, `win32/` | OS glue (timers, virtual filesystem, COM, registry) |
| `memory-lib/` | Custom allocators / memory tracking |
| `render/` | DirectX 9 renderer + HLSL shader sources (`Shaders/`, `OnlineShaders/`) |
| `scene/` | Scene graph, transformations, culling |
| `terrain/` | Heightfield + tile terrain, road meshes, LOD |
| `sound/` | FMOD wrapper |
| `network/`, `net/` | Low-level sockets + higher-level RPC |
| `libdb/`, `libdb-net/` | MySQL/network DB access |
| `ui/` | C++ UI runtime that hosts the Flash UI |
| `nival-input/` | Input abstraction |
| `game/PF/`, `game/PW/` | Gameplay logic — units, abilities, talents, AI |
| `pf-game-logic/` | Higher-level gameplay (lobby flow, adventure screens) |
| `pf-minigames/` | Mini-games embedded in heroes / talents |
| `types/`, `pf-types/`, `social-types/`, `pf-types-db/`, `social-types-db/`, `types-db/` | C# **type definitions** consumed by the data-binding code generator. Not C++ runtime — this is the schema layer that backs the `.xdb` serialization format and the editor's object browser |
| `scripts/` | Lua VM integration + Tamarin (AS3) bridge |
| `samples/` | Standalone demo programs (SimpleGame, IRC, RemoteObjects, Thrift) |
| `PF.sln`, `SocialTypes_12.sln`, `CMakeLists.txt` | Build entry points |

**Builds with:** CMake (the `CMakeLists.txt` at the engine root is the union
build) **or** Visual Studio via `PF.sln`. The two trees are partially
overlapping but not interchangeable — see [§6](#6-known-structural-debts).

### 2.4 `editor/`

PF_Editor — the in-house editor used by designers to edit `.xdb` data,
particle systems, materials, level layouts, tutorial scripts, and so on.

| Sub-tree | Purpose | Language |
|----------|---------|----------|
| `src/pf-editor` | Main editor app (WinForms shell) | C# |
| `src/pf-editor-c` | Console-mode build (used by automation / CI) | C# |
| `src/pf-editor-native` | C++ side: rendering / FMOD interop hosted in the editor | C++ |
| `src/editor-lib`, `src/editor-native`, `src/editor-plugins` | Reusable editor libraries and plugins | C# / C++ |
| `src/easel-level-editor` | Level / map editor | C# |
| `src/db-code-gen` | Generates C++/C# accessors from the `engine/types/*.cs` schemas | C# |
| `src/formula-builder` | Formula DSL editor (talents, balance) | C# |
| `src/pf-type-icons` | Icons used by the object browser | resources |
| `editor/build` | Holds editor config (`config.txt`, `pw_game_lang.ini`) — the actual `PF_Editor.exe` ships in `client/build/Bin/` |

**Entry point:** `client/build/Bin/PF_Editor.exe` (despite living under `client/build`).
**Builds with:** MSBuild via `*.csproj` / `*.vcxproj`.

### 2.5 `tools/`

A flat folder of ~80 developer / ops utilities. Group by purpose:

| Group | Tools |
|-------|-------|
| **Build & code-gen** | `CMakeGenerator`, `CodeGenRPC`, `FilePileCompiler`, `DBCodeGen` (also at `client/build/Bin/DBCodeGen.exe`), `CCompiler`, `FixSln`, `RepairVersion`, `GetRevision`, `SVNGlobalIgnoreSetter` |
| **Asset pipeline** | `mesh-converter` (COLLADA→`.stat`), `shader-compiler` (HLSL→DDS), `MayaPlugins`, `MayaScripts`, `maya-extension`, `maya-exe-interaction`, `blender-export`, `PaintGenerator`, `TextureDupChecker`, `XdbTools`, `CopyReference`, `River`, `Map`, `MapEditor`, `MapTreeConvertor`, `Reimport*`, `ZDATAChecker` |
| **Diagnostics** | `LogAnalyzer`, `LagLogViewer`, `DebugVarStatView`, `MemoryMonitor`, `SymbolServer`, `PerformanceLog*`, `DXResourcesLeaks.rb`, `RenderSequenceLog.rb`, `SQLRemotePerfChecker`, `UdpDiag`, `analyzecrashstack.pl`, `processCRCItemDump.pl` |
| **Testing** | `Autotest`, `AutotestOld`, `TestFramework` (CxxTest), `InnoTest` (installer test), `CrashRptTest`, `CxxTest`, `Checkers` |
| **Live ops** | `Billing`, `GMTools`, `ChatTool`, `Censor` (profanity filter), `LiveMMakingTool`, `CastleDataDaemon`, `RollTestTool`, `ServerAdminTools`, `ReleaseNotesSender` |
| **Localization** | `Localization`, `LocKit`, `PWLocalization` |
| **Setup / fetch (post-restructure)** | `setup/setup.ps1` (junctions + LFS fetch), `assets/fetch_assets.py` (Google Drive mirror) |

**Builds with:** Mostly Visual Studio per-tool `.sln`; a few are scripts
(Python, Ruby, Perl, batch).

### 2.6 Data folders

| Folder | Role |
|--------|------|
| `assets/` | Runtime data the binaries load: `.xdb` (object DB), `.dds`/`.tga` (textures), `.anim`/`.skin`/`.skel` (animation), `.stat`/`.mayastat` (geometry), `.fsb` (FMOD banks), `.lua` (gameplay scripts), compiled shaders. Subdomains: `heroes/`, `creeps/`, `buildings/`, `items/`, `summons/`, `pets/`, `critters/`, `maps/`, `terrain/`, `effects/`, `ui/`, `gfx-textures/`, `audio/`, `shaders/`, `faces/`, `glyphs/`, `dialogs/`, `mini-games/`, `impulses/`, `game-logic/`, `social/`, `scripts/`, `debug/`, `tech/`, `server-data/`, `test/` |
| `assets-source/` | Editable source art (PSD, PNG, source FBX/Maya files) that compiles into `assets/`. Pairing convention: `assets-source/styles/Icons/Talents/Foo.png` → `assets/ui/Styles/Icons/Talents/Foo.dds`. |
| `localization/` | Per-locale strings + voice-over (`en-US`, `ru-RU`, `de-DE`, `fr-FR`, `tr-TR`, `lt-LT`, `pl-PL`, `vi-VN`, `ru-MO`) |
| `profiles/` | Runtime configuration — `game.cfg` (client), `private.cfg_example` (cheats), type hashes |

### 2.7 `vendor/`

~2 GB of third-party libraries, mostly pre-built. Headline entries: Boost,
DirectX, FMOD, CEF, Maya, wxWidgets, Steam, ACE_wrappers, xulrunner-sdk,
Tamarin, MySQL, Thrift, OpenSSL, libcurl, CrashRpt, SharpSvn, ircdotnet,
Terabit, DirectSSN. Engine and tool builds resolve includes / libs from here.

## 3. Build artefacts

What lives where after a successful build, and which source tree produces it:

| Binary | Source | Built with |
|--------|--------|------------|
| `client/build/Bin/PW_Game.exe` | `client/src/pw-game` + `engine/` | VS (`.vcproj`) — game client |
| `client/build/Bin/PW_MiniLauncher.exe` | `client/src/pw-mini-launcher` | VS — first-run launcher |
| `client/build/Bin/PF_Editor.exe`, `PF_EditorC.exe` | `editor/src/pf-editor*` + `engine/` | MSBuild (C#) + VS (C++) |
| `client/build/Bin/DBCodeGen.exe` | `editor/src/db-code-gen` | MSBuild |
| `client/launcher/v1.5/Launcher/PWLauncher.exe` | `client/launcher` | VS |
| `client/flash-ui/*.swf` | `client/flash-ui/*.fla`, `src/`, `classes/` | Flash IDE / Tamarin |
| `server/battle/build/Bin/UniServerApp*.cmd` + `Bin/*.dll/.exe` | `server/battle/src/Server` + `engine/` | VS / CMake |
| `server/social/*` | `server/social` | Python (interpreted) |
| `server/socagr/www`, `application/` | `server/socagr` | PHP (interpreted) |
| `server/control-center/ClusterManagement` | same | MSBuild |
| `tools/*/` | per-tool source | per-tool build |

## 4. Runtime data flow

Two main scenarios.

**Solo / lobby launch** (`local_game 1` in `profiles/game.cfg`):
1. `PW_Game.exe` starts, reads `Profiles/game.cfg` (junction → `profiles/`).
2. Loads core engine subsystems (render, sound, scripts, UI).
3. Discovers data via the virtual filesystem rooted at `Data/` (junction → `assets/`).
4. Hosts Flash UI from `client/flash-ui/main.swf` for menus.
5. On match start, simulates the battle in-process — no server traffic.

**PvP launch** (`local_game 0` + `login_adress`):
1. Client logs in via `99UniServerApp-login.cmd` role of the battle cluster.
2. Authenticates against `server/social` (via Thrift / HTTP).
3. Lobby + matchmaking handled by `server/social/coordinator.py` and
   `livemm` / `lobby` server roles.
4. Match creation: `gamesvc` role spawns a battle simulation; client connects
   via `relay`.
5. During a match, battle server is authoritative — broadcasts world state
   to clients; clients send input.
6. Aggregator / billing / GM events go through `server/socagr` (PHP).

## 5. Inter-module dependencies

Coarse-grained graph (arrow = "depends on"):

```
client/src         engine/  --->  vendor/
   |                  ^
   v                  |
client/flash-ui    server/battle/src
                      ^
editor/src    -------- (engine/types schemas)
                      ^
tools/*       --------+

server/social  --->  vendor/python-libs (Tornado, Thrift)
server/socagr  --->  vendor/php-libs (Zend)
server/control-center --->  .NET FX
```

Notes:
- `engine/types/*.cs` is the **schema** for `.xdb` data — both runtime
  serialization (C++) and editor (C#) read from it via generated code
  (`db-code-gen`).
- `server/battle/build/Data` duplicates `assets/`; treat `assets/` as source
  of truth and re-mirror as needed.
- `client/build/` and `editor/build/` overlap — `PF_Editor.exe` ships under
  `client/build/Bin/` because it is co-installed with the client.

## 6. Known structural debts

These are tracked separately in
[REFACTORING_PLAN.md](REFACTORING_PLAN.md). Highlights:

1. **Build path drift.** `engine/CMakeLists.txt` still references
   `${SRC_DIR}/../Vendor` (capitalised, old layout). PF.sln + many
   `.vcxproj` carry pre-restructure relative paths.
2. **Hard-coded `Data/` strings.** Many C++ sites resolve paths via literal
   `"Data/..."`; the runtime junctions paper this over but it is fragile.
3. **Dual data tree.** `assets/` and `server/battle/build/Data` are 25 k
   duplicate `.xdb` files. Should be a build-time copy or symlink.
4. **Pre-restructure casing.** Six folders inside `assets/` need
   case-sensitive aliases (`GameLogic`, `MiniGames`, `GFX_Textures`,
   `Server`, `Dialog`, `SocialTest`) — fixed by `tools/setup/setup.ps1`,
   but a real fix is to update the path resolver in C++.
5. **Two overlapping build systems** (CMake vs `PF.sln`) for `engine/` —
   pick one as canonical.
6. **Old solution formats.** `.vcproj` (VS2008) survives next to
   `.vcxproj` (VS2010+). Either upgrade or document the version lock.
7. **Server-side Python is Python 2-era.** `server/social/*.py` mixes
   Tornado/Thrift idioms from the late 2000s. Migration path TBD.
