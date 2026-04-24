# Prime-World — first-run setup

This guide takes a fresh Windows machine from `git clone` to a running
`PW_Game.exe` offline lobby.

## Prerequisites

- Windows 10/11 (junctions are a Windows concept).
- [Git](https://git-scm.com/download/win).
- Python 3.8+ — Windows 10+ ships `py`; Linux/macOS have `python3`. Standard
  library only, no `pip install` required.
- Windows PowerShell 5.1 (ships with Windows) or PowerShell 7+.
- ~20 GB free disk.

> **Git LFS is no longer used.** Heavy binaries are distributed as Google
> Drive zip archives via `tools/assets/fetch_assets.py`. You do **not** need
> `git-lfs` installed, and you do **not** need to set `GIT_LFS_SKIP_SMUDGE`.
> If you have an old clone where the LFS filter is still installed, see
> [Cleaning up an old Git LFS clone](#cleaning-up-an-old-git-lfs-clone) below.

## Steps

### 1. Clone the repository

```powershell
git clone https://github.com/meonisk/Prime-World.git
cd Prime-World
```

A fresh clone is ~200 MB — code and metadata only.

### 2. Fetch the heavy binaries

The game cannot launch without the runtime assets (textures, audio, models,
maps), and a few large vendor binaries (`vendor/CEF/libcef.dll`,
`vendor/Maya/...`, `vendor/Tamarin/...`) are also off-repo.

```powershell
py tools\assets\fetch_assets.py --all
```

This fetches all archives (~10 GB). For a minimal launchable client only:

```powershell
py tools\assets\fetch_assets.py
```

See [tools/assets/README.md](../tools/assets/README.md) and
[tools/assets/manifest.json](../tools/assets/manifest.json) for the full list
of archives, sizes, and per-tag selection (`--tag=assets`, `--tag=vendor`,
`--tag=misc`, `--tag=source`, `--tag=locale`).

### 3. Run the bootstrap

```powershell
powershell -ExecutionPolicy Bypass -File tools\setup\setup.ps1
```

The script (see [tools/setup/README.md](../tools/setup/README.md) for
details):

1. Creates the runtime junctions the prebuilt `PW_Game.exe` expects.
   Without these the binary crashes looking for pre-restructure folder names
   (`GameLogic/`, `GFX_Textures/`, `Server/`, `Dialog/`, `MiniGames/`,
   `SocialTest/`) and missing `Data/`, `Localization/`, `Profiles/` next to
   `Bin/`.
2. Sanity-checks the 11 large binaries that used to live on Git LFS — if any
   are still 133-byte pointer stubs, prints a one-line hint to re-run
   `fetch_assets.py`.

Re-run with `-Check` any time to verify state without changes:

```powershell
powershell -ExecutionPolicy Bypass -File tools\setup\setup.ps1 -Check
```

### 4. Switch the client to offline mode

Edit `profiles\game.cfg` and change `local_game 0` to `local_game 1`. This
skips the login-server handshake and boots straight into the lobby.

### 5. Launch the game

```powershell
client\build\Bin\PW_Game.exe
```

You should see the lobby. Pick a map (e.g. `Maps/Multiplayer/MidOnly`), pick
a hero, click Start Session — a battle loads.

## Troubleshooting

### `PW_Game.exe` aborts with `DbResourceCache::Precache: Cannot open file`
Junctions are missing or point to the wrong target. Run `setup.ps1 -Check`
and follow its output. If a real directory sits where a junction should be
(e.g. someone checked out `assets/Dialog/` without the junction), move its
contents into the kebab-case sibling (`assets/dialogs/`) and re-run with
`-Force`.

### `setup.ps1` reports a file as a "133-byte LFS pointer stub"
You have an old clone where Git LFS smudged a pointer file in. Re-run
`tools\assets\fetch_assets.py --all` — it overwrites the stubs with the
real binaries from Google Drive. (If the stub also appears in `git status`
as modified, see the next section.)

### `ExecutionPolicy` blocks the script
The command lines above pass `-ExecutionPolicy Bypass` explicitly; it only
applies to that single run. You can also permanently allow local scripts
with `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` if you prefer.

## Cleaning up an old Git LFS clone

If you cloned the repo before LFS was retired, your local `.git/config` may
still have a `[lfs]` section, an `lfs.url` pointing at an upstream, and the
`filter.lfs.*` smudge/clean filters installed. None of these are needed any
more, and they can cause spurious LFS calls on every push.

To clean up:

```powershell
# Remove the filter.lfs.* hooks from this repo's .git/config
git lfs uninstall --local

# Drop the now-orphan lfs.url and any per-endpoint sections
git config --unset lfs.url
git config --remove-section "lfs `"https://github.com/nival/Prime-World.git/info/lfs`""
git config --remove-section lfs
```

The last two commands may report "no such section" — that is fine. Verify
with `git config --local --list | findstr /I lfs` (Windows) or
`git config --local --list | grep -i lfs` (Linux/macOS): the output should
be empty.

After this, pushes go directly to your origin without any LFS-related
authentication detours.

## What to expect on first launch

- ~30 seconds cold start, RAM ~150–500 MB.
- The log reports `Mouse captured by 'fairy'` etc. as you hover heroes.
- Warnings about missing `_sans` font and a couple of
  `Items/Talents/.../compiledDescription*.txt` files are cosmetic.
- `local_game 1` skips the login server; for PvP see the README.

## Known issues

### Bots via `profiles/private.cfg` — broken on this prebuilt

README's "Launch the Game with Bots" recipe (`add_ai bots` in the
`AT THE GAME BEGINNING` section of `private.cfg`) does not work with
`client/build/Bin/PW_Game.exe`. Most directives in `private.cfg_example`
(`custom`, `lobby`, `login`, `ready`, `waitWorldStep`,
`debug_disable_world_crc`, `settings`) log as `Unknown command or variable`
— they appear to be compiled out of this binary.

`add_ai` itself is a `REGISTER_DEV_CMD` registered only after
`AdventureScreen` loads (see `engine/pf-game-logic/AdventureScreen.cpp:7151`
— the handler returns early while `world->GetStepNumber() < 0`). So it
cannot fire from a boot-time script.

**Workaround:** launch normally, enter a battle through the lobby, then
press **`~` (tilde)** in-game and type `add_ai bots`. Valid filters: `all`,
`self`, `others`, `friends`, `enemies`, `humans`, `bots`, `mid`.

To investigate later: whether a different start-up script hook (e.g.
`autoexec.cfg` — the binary reports it missing at boot) can queue a command
to fire once `AdventureScreen` is active.

## Related docs

- [tools/setup/README.md](../tools/setup/README.md) — script options
- [tools/assets/README.md](../tools/assets/README.md) — asset-fetch flow and manifest format
- [docs/REPO_STRUCTURE.md](REPO_STRUCTURE.md) §6.2 — why junctions are needed
- [README.md](../README.md) — overview, PvP launch, cheats
