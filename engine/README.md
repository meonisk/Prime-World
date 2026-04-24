# engine/

The shared C++ game engine. Linked into `PW_Game.exe`, the battle server, the
editor, and several tools. This is the bulk of the C++ in the repository.

## Subsystems

| Folder | Purpose |
|--------|---------|
| `core/`, `pf-core/` | Base primitives — strings, containers, smart pointers, IO, threading |
| `system/`, `win32/` | OS glue — timers, virtual filesystem, COM, registry |
| `memory-lib/` | Custom allocators / memory tracking |
| `render/` | DirectX 9 renderer + HLSL sources (`Shaders/`, `OnlineShaders/`) |
| `scene/` | Scene graph, transformations, culling |
| `terrain/` | Heightfield + tile terrain, road meshes, LOD |
| `sound/` | FMOD wrapper |
| `network/`, `net/` | Sockets + higher-level RPC |
| `libdb/`, `libdb-net/` | MySQL access (network DB layer) |
| `ui/` | C++ UI runtime that hosts the Flash UI |
| `nival-input/` | Input abstraction (mouse, keyboard, gamepad) |
| `game/PF/`, `game/PW/` | Gameplay core — units, abilities, talents, AI |
| `pf-game-logic/` | Higher-level gameplay (lobby flow, AdventureScreen) |
| `pf-minigames/` | Mini-games embedded in talents / heroes |
| `types/`, `pf-types/`, `social-types/`, `pf-types-db/`, `social-types-db/`, `types-db/` | **C# type schemas** consumed by `db-code-gen`. They define the `.xdb` object model used by both runtime serialization (C++) and the editor (C#). Not C++ runtime code |
| `scripts/` | Lua VM integration; Tamarin (AS3) bridge |
| `samples/` | Standalone demos (SimpleGame, IRC, RemoteObjects, Thrift) |

## Build entry points

| File | Toolchain | Notes |
|------|-----------|-------|
| `CMakeLists.txt` | CMake 2.6+ | Union build; references `../Vendor` (pre-restructure path — see [REFACTORING_PLAN.md](../docs/REFACTORING_PLAN.md) Phase 1) |
| `PF.sln` | Visual Studio (mix of `.vcproj`/`.vcxproj`) | Monolithic VS solution |
| `SocialTypes_12.sln` | Visual Studio | Schemas for the social backend |
| `Application.{ico,manifest,rc}`, `ApplicationResources.h`, `App.ico`, `Version.{h,rc,h.xslt}`, `Version.h.xslt`, `CommonAssemblyInfo.cs*` | Resource / version glue | Shared across binaries |
| `run_cmake.bat` | helper | Invokes CMake |
| `PF_Version.config` | versioning | Read by `Version.h.xslt` |

The CMake and Visual Studio trees overlap but are not interchangeable — see
[REFACTORING_PLAN.md](../docs/REFACTORING_PLAN.md) Phase 1.

## Dependencies

- `vendor/` — DirectX, FMOD, Boost, ACE_wrappers, Thrift, OpenSSL, MySQL, Tamarin, CxxTest, zlib, xulrunner-sdk.
- Has **no** dependency on `client/`, `server/`, `editor/`, or `tools/` — those depend on it.

## See also

- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) §2.3
- [docs/REFACTORING_PLAN.md](../docs/REFACTORING_PLAN.md) — staged cleanup plan
