# ClipPress — Video Compressor

<p align="center">
  <img src="https://img.shields.io/github/v/release/kamalalhagh/ClipPress?style=flat-square&color=FF6B6B" alt="Release">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS-blue?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.12-brightgreen?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/author-Kevin%20Haji-FF6B6B?style=flat-square" alt="Author">
</p>

A bilingual (English / Persian) desktop app that compresses any video to a compact MP4 using FFmpeg. Three presets cover everything from social-media sharing to archival quality — no command line, no setup.

**[Download latest release](https://github.com/kamalalhagh/ClipPress/releases/latest)** | **[README فارسی](README.fa.md)**

---

## Features

- Three compression presets — Maximum (720p), Medium (1080p), Low (1080p high quality)
- English / Persian UI with correct RTL rendering
- Dark and light theme
- FFmpeg is bundled — works out of the box on every supported platform
- Real-time progress bar showing live conversion percentage
- Accepts MP4, MOV, MKV, AVI, WMV, WEBM, FLV, M4V, TS and more

---

## Download

| Platform | File |
|----------|------|
| Windows Intel / AMD | `ClipPress-windows-x64.exe` |
| Windows ARM64 | `ClipPress-windows-arm64.exe` |
| macOS Universal (recommended) | `ClipPress-macOS-universal` |
| macOS Apple Silicon | `ClipPress-macOS-arm64` |
| macOS Intel | `ClipPress-macOS-intel` |

On macOS, run this once after downloading:

```bash
chmod +x ClipPress-macOS-*
xattr -d com.apple.quarantine ClipPress-macOS-*
```

---

## Compression Presets

| Level | Resolution | CRF | Preset | Audio | Best for |
|-------|------------|-----|--------|-------|----------|
| Maximum | 720p | 28 | slow | AAC 128k | Sharing, social media |
| Medium | 1080p | 23 | medium | AAC 192k | General use |
| Low | 1080p | 18 | fast | AAC 256k | Archiving |

---

## Running from Source

```bash
git clone https://github.com/kamalalhagh/ClipPress.git
cd ClipPress
pip install -r requirements.txt
python main.py
```

Python 3.9 or later required. FFmpeg must be in PATH, or the app will offer to install it on first launch.

---

## Author

**Kevin Haji** — [kevinhaji.com](https://kevinhaji.com) · [github.com/kamalalhagh](https://github.com/kamalalhagh)

---

## License

MIT © [Kevin Haji](https://kevinhaji.com)
