# FMOD Designer installers

The six `fmoddesigner*win-installer.exe` installers used to live in
`vendor/fmod/fmoddesigner/`. They have been removed from git entirely — they
added ~180 MB to every clone and are publicly available from the vendor.

| Version | Original filename | Upstream source |
|---------|-------------------|-----------------|
| 4.32.05 | `fmoddesigner43205win-installer.exe` | https://www.fmod.com/download (legacy FMOD Designer archive) |
| 4.34.05 | `fmoddesigner43405win-installer.exe` | https://www.fmod.com/download (legacy FMOD Designer archive) |
| 4.44.04 | `fmoddesigner44404win-installer.exe` | https://www.fmod.com/download (legacy FMOD Designer archive) |
| 4.44.09 | `fmoddesigner44409win-installer.exe` | https://www.fmod.com/download (legacy FMOD Designer archive) |
| 4.44.17 | `fmoddesigner44417win-installer.exe` | https://www.fmod.com/download (legacy FMOD Designer archive) |
| 4.44.19 | `fmoddesigner44419win-installer.exe` | https://www.fmod.com/download (legacy FMOD Designer archive) |

If you need one of these installers, download it from FMOD and drop it back
into `vendor/fmod/fmoddesigner/` locally; the gitignore rule `/vendor/fmod/`
will keep it out of commits.

The rest of the prebuilt FMOD payload (SDK libraries and DLLs) is delivered
via `pw-vendor-prebuilt.zip`; see `tools/assets/manifest.json`.
