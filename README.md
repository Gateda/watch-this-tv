# Watch This — Fire TV App Build Guide

This wraps `index-9-1.html` in a Capacitor Android shell so it installs as a real app
on Fire OS devices (Fire TV Cube, older Fire TV Sticks, Fire TVs built into smart TVs).

This targets **Fire OS** (Android-based), not the newer **Vega OS** (2025–2026 Fire TV
Stick HD / 4K Select) — those need a separate build using Amazon's Vega SDK, which is
still in open beta. Worth checking which Fire TV hardware you actually have before
building; if you're not sure, `Settings > My Fire TV > About` tells you the OS.

This whole thing runs on your own machine, not in this chat — you'll need Node.js,
Android Studio (for the SDK + build tools), and a JDK installed locally.

---

## 0. Prerequisites

- Node.js (LTS) — https://nodejs.org
- Android Studio — https://developer.android.com/studio (installs the Android SDK;
  during setup, accept the SDK license and let it install build-tools + platform-tools)
- JDK 17 (Android Studio bundles one; if `java -version` doesn't already show 17+, use
  the one under Android Studio's own JBR, or install one separately)

## 1. Create the project

```bash
mkdir watch-this-tv && cd watch-this-tv
npm init -y
npm install @capacitor/core @capacitor/cli @capacitor/android
```

## 2. Drop in the provided files

Copy everything from this scaffold into your new `watch-this-tv/` folder:
- `capacitor.config.json` → project root
- `www/index.html` → project root (this is your app file, already renamed to
  `index.html` since Capacitor expects that as the entry point)

Whenever you update the app from our chat later, just overwrite `www/index.html`
with the new version and re-run steps 4–6 below — no other changes needed.

## 3. Add the Android platform

```bash
npx cap add android
npx cap sync
```

This generates an `android/` folder — a full Android Studio project.

## 4. Fire TV-specific manifest changes

Open `android/app/src/main/AndroidManifest.xml` and edit it to match
`android-manifest-snippet.xml` (included here) — specifically:
- Add `android:banner="@drawable/banner"` to `<application>`
- Add the `LEANBACK_LAUNCHER` category to the main activity's intent filter
- Set `android:screenOrientation="landscape"`
- Confirm `<uses-permission android:name="android.permission.INTERNET" />` is present
  (Capacitor adds this by default, but double check)

You'll also need a 320×180 PNG banner image — any simple logo/wordmark on your dark
background works — saved at `android/app/src/main/res/drawable/banner.png`. Without
it, Fire TV may not show a proper home-screen tile for the app.

## 5. Build the APK

```bash
cd android
./gradlew assembleDebug
```

(On Windows, use `gradlew.bat assembleDebug`.)

First build takes a while — Gradle downloads dependencies. Output lands at:
```
android/app/build/outputs/apk/debug/app-debug.apk
```

A debug build is fine for personal sideloading — no need to deal with release signing
or the Amazon Appstore unless you want to distribute it publicly later.

## 6. Get it onto your Fire TV

Two ways — pick whichever's easier:

**Option A — Downloader app (simplest, no computer-to-TV cable needed)**
1. On the Fire TV, install "Downloader" from the Appstore if you don't have it.
2. Host `app-debug.apk` somewhere reachable by URL — easiest is dropping it in the same
   Netlify site alongside `index-9-1.html`, or any simple file host.
3. On the Fire TV, open Downloader, type in that URL, and let it download + install.

**Option B — ADB over your network**
1. On the Fire TV: `Settings > My Fire TV > Developer Options` → turn on
   "ADB Debugging" (enable Developer Options first via 7 taps on the Software Version
   entry under About, if you don't see Developer Options yet).
2. Find the Fire TV's IP address: `Settings > My Fire TV > About > Network`.
3. From your computer (with Android platform-tools/adb installed):
   ```bash
   adb connect <FIRE_TV_IP>:5555
   adb install android/app/build/outputs/apk/debug/app-debug.apk
   ```

## 7. Test with the actual remote

Launch the app and check:
- Arrow keys/D-pad move focus visibly between chips, buttons, and game cards
- Select/Enter opens the watch link on a focused card
- Back closes the "Where I Watch" panel if it's open
- Text is legible from your actual couch distance

## 8. Iterating later

Every time the HTML file gets updated in our chat:
```bash
cp /path/to/new/index-9-1.html watch-this-tv/www/index.html
cd watch-this-tv
npx cap sync
cd android && ./gradlew assembleDebug
```
Then reinstall via whichever method you used in step 6 — Android will just update the
existing app in place (same package ID), no need to uninstall first.
