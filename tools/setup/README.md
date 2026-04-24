# tools/setup — first-run bootstrap

`setup.ps1` makes a fresh clone of the repository runnable by creating the
runtime junctions the prebuilt `PW_Game.exe` expects:

- `client/build/{Data,Localization,Profiles}` → repo-root `assets/`,
  `localization/`, `profiles/`
- `assets/{GameLogic,MiniGames,GFX_Textures,Server,Dialog,SocialTest}` →
  their kebab-case counterparts (`game-logic/`, `mini-games/`,
  `gfx-textures/`, `server-data/`, `dialogs/`, `social-test/`)

It also performs a sanity check: a handful of large binaries used to live on
Git LFS, and on a fresh clone they may still appear as 133-byte LFS pointer
stubs if a previous setup left them behind. If so, the script points at
`python tools/assets/fetch_assets.py --all`, which mirrors all heavy
binaries from Google Drive (see [`tools/assets/manifest.json`](../assets/manifest.json)).

## Usage

```powershell
# full bootstrap
powershell -ExecutionPolicy Bypass -File tools\setup\setup.ps1

# verify state only, no changes
powershell -ExecutionPolicy Bypass -File tools\setup\setup.ps1 -Check

# force-recreate junctions (when one is pointing somewhere else)
powershell -ExecutionPolicy Bypass -File tools\setup\setup.ps1 -Force
```

## Notes

- Idempotent: safe to re-run. Existing correct junctions are skipped.
- Refuses to delete a real directory where a junction is expected — manual
  cleanup is required first.
- `ExecutionPolicy Bypass` is needed because scripts are blocked by default
  on Windows; it only applies to this single run.
- The script does **not** modify `.git/config`, source files, or the git
  index. It only creates filesystem junctions and prints diagnostics.

## Files touched

- On-disk junction entries under `client/build/` and `assets/`.
- Nothing else.

## Related docs

- [docs/SETUP.md](../../docs/SETUP.md) — full first-run guide
- [tools/assets/README.md](../assets/README.md) — heavy-binary fetch flow
