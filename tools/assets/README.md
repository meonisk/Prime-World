# tools/assets

Helpers for managing the large binary archives that live outside git.

| File | Purpose |
|------|---------|
| `manifest.json` | Canonical list of external archives: name, tag, Google Drive file id, sha256, size, source paths. |
| `fetch_assets.py` | Downloads archives from Google Drive, verifies sha256, extracts them into the repo root. Used by contributors after `git clone`. |
| `build_archives.py` | Rebuilds the zip archives from a working tree that still contains the large files. Used once by maintainers before history is rewritten, and later whenever the archives need to be refreshed. |
| `paths_to_purge.txt` | Path list consumed by `git-filter-repo --paths-from-file --invert-paths` when rewriting history to physically drop the large blobs. |

## Typical flows

**Contributor: get a runnable repo**
```
pip install gdown tqdm
python tools/assets/fetch_assets.py --all          # everything
python tools/assets/fetch_assets.py                # required-only (engine/editor runtime)
python tools/assets/fetch_assets.py --tag=assets   # just the game assets
python tools/assets/fetch_assets.py --tag=vendor   # just third-party prebuilt libs
```

**Maintainer: publish a new archive set**
```
python tools/assets/build_archives.py              # produces dist/assets-archives/*.zip + sha256
# upload zips to the public Google Drive folder
# paste file ids + sha256 + size_bytes into manifest.json
git commit tools/assets/manifest.json
```

**Maintainer: purge large blobs from git history** (destructive, separate session)
```
git clone --mirror <repo-url> prime-world-backup.git      # backup first
pip install git-filter-repo
git filter-repo --invert-paths --paths-from-file tools/assets/paths_to_purge.txt --force
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git remote add origin <repo-url>
git push --force --all && git push --force --tags
```
