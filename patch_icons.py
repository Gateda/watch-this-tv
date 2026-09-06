#!/usr/bin/env python3
"""
Drops the Watch This launcher icon into the freshly-generated Capacitor Android project.

Runs after `npx cap sync android` (which regenerates the android/ folder from scratch on
every build, wiping out any icon changes from the last run) and before `./gradlew
assembleDebug` — same pattern as patch_manifest.py and patch_native_plugin.py.

Expects a repo-root icons/ folder containing these 10 files (the exact set from the
icon zip already generated for this app):
  ic_launcher_mdpi_48.png        ic_launcher_round_mdpi_48.png
  ic_launcher_hdpi_72.png        ic_launcher_round_hdpi_72.png
  ic_launcher_xhdpi_96.png       ic_launcher_round_xhdpi_96.png
  ic_launcher_xxhdpi_144.png     ic_launcher_round_xxhdpi_144.png
  ic_launcher_xxxhdpi_192.png    ic_launcher_round_xxxhdpi_192.png

Copies each into android/app/src/main/res/mipmap-<density>/ic_launcher.png (and
ic_launcher_round.png), overwriting Capacitor's default placeholder icon.

Also deletes res/mipmap-anydpi-v26/ — that's Capacitor's default *adaptive* icon (a
vector foreground/background pair, not a bitmap). On API 26+ that adaptive version wins
over the plain PNGs below no matter what's in them, so leaving it in place would mean
the placeholder keeps showing on newer Android/Fire OS versions even after this script
runs. Deleting it makes every API level fall back to the density-specific PNGs instead.
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).parent
ICONS_DIR = ROOT / "icons"
RES_DIR = ROOT / "android" / "app" / "src" / "main" / "res"

DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}


def copy_icon(src_name, dest_dir, dest_name):
    src = ICONS_DIR / src_name
    if not src.exists():
        print(f"  SKIP (not found): {src}")
        return False
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest_dir / dest_name)
    print(f"  {src.name} -> {dest_dir / dest_name}")
    return True


def main():
    if not RES_DIR.exists():
        raise SystemExit(f"Android res folder not found at {RES_DIR} — run this after `npx cap sync android`.")
    if not ICONS_DIR.exists():
        raise SystemExit(f"No icons/ folder found at {ICONS_DIR} — add your icon PNGs there first.")

    print("Copying launcher icons into mipmap-* folders...")
    ok = True
    for density, size in DENSITIES.items():
        dest_dir = RES_DIR / f"mipmap-{density}"
        ok &= copy_icon(f"ic_launcher_{density}_{size}.png", dest_dir, "ic_launcher.png")
        ok &= copy_icon(f"ic_launcher_round_{density}_{size}.png", dest_dir, "ic_launcher_round.png")

    adaptive_dir = RES_DIR / "mipmap-anydpi-v26"
    if adaptive_dir.exists():
        shutil.rmtree(adaptive_dir)
        print(f"Removed {adaptive_dir} so API 26+ falls back to the bitmap icons above.")

    if not ok:
        raise SystemExit("One or more icon files were missing — check the icons/ folder against the list in this script's docstring.")
    print("Done.")


if __name__ == "__main__":
    main()
