# Screenplay Cards — Desktop App

## Setup

Requires Node.js — download from https://nodejs.org (LTS version).

```bash
# 1. Install dependencies (one time)
npm install

# 2. Run in development
npm start

# 3. Build .dmg for distribution
npm run build
```

Built .dmg appears in the `dist/` folder.

## App icon

Place a 1024x1024 PNG named `icon.png` in the `assets/` folder, then run:

```bash
mkdir assets/icon.iconset
sips -z 16 16     assets/icon.png --out assets/icon.iconset/icon_16x16.png
sips -z 32 32     assets/icon.png --out assets/icon.iconset/icon_16x16@2x.png
sips -z 32 32     assets/icon.png --out assets/icon.iconset/icon_32x32.png
sips -z 64 64     assets/icon.png --out assets/icon.iconset/icon_32x32@2x.png
sips -z 128 128   assets/icon.png --out assets/icon.iconset/icon_128x128.png
sips -z 256 256   assets/icon.png --out assets/icon.iconset/icon_128x128@2x.png
sips -z 256 256   assets/icon.png --out assets/icon.iconset/icon_256x256.png
sips -z 512 512   assets/icon.png --out assets/icon.iconset/icon_256x256@2x.png
sips -z 512 512   assets/icon.png --out assets/icon.iconset/icon_512x512.png
sips -z 1024 1024 assets/icon.png --out assets/icon.iconset/icon_512x512@2x.png
iconutil -c icns assets/icon.iconset -o assets/icon.icns
```

## Project files

Each project saves as a `.screenplaycards` file — a JSON file you can store anywhere.
Double-clicking a `.screenplaycards` file opens it directly in the app.

## Auto-updates

Updates are served via GitHub Releases at github.com/petercarrillo/screenplay-cards.
To release an update:
1. Bump `version` in `package.json`
2. Run `npm run build`
3. Create a GitHub Release and upload the `.dmg` and `latest-mac.yml` from `dist/`

## Code signing

Without signing, users see an "unidentified developer" warning once.
They can right-click → Open to bypass it.
For proper signing you need an Apple Developer account ($99/year).
