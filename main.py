"""
ClipPress / کلیپ‌پرس
Video Compressor — Windows Desktop App

Author  : Kevin Haji
Website : https://kevinhaji.com
GitHub  : https://github.com/kamalalhagh
Repo    : https://github.com/kamalalhagh/ClipPress
License : MIT
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os
import sys
import re
import webbrowser
import urllib.request
import zipfile
import shutil
import tempfile
import json

if sys.platform == "win32":
    import winreg
    import ctypes

# ── Platform helpers ──────────────────────────────────────────────────────────
_WIN = sys.platform == "win32"
_MAC = sys.platform == "darwin"
_EXE = "ffmpeg.exe" if _WIN else "ffmpeg"

# ── Persian / RTL rendering ───────────────────────────────────────────────────
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_BIDI = True
except ImportError:
    HAS_BIDI = False


def _fix_rtl(text: str) -> str:
    if not HAS_BIDI or not text:
        return text
    lines = text.split('\n')
    out = []
    for line in lines:
        if line.strip():
            out.append(get_display(arabic_reshaper.reshape(line)))
        else:
            out.append(line)
    return '\n'.join(out)


def _preprocess_fa():
    for key, val in T["fa"].items():
        if isinstance(val, str):
            T["fa"][key] = _fix_rtl(val)
        elif isinstance(val, list):
            T["fa"][key] = [
                tuple(_fix_rtl(s) if isinstance(s, str) else s for s in item)
                if isinstance(item, tuple) else item
                for item in val
            ]

# ── Palette ───────────────────────────────────────────────────────────────────
ACCENT       = "#FF6B6B"
ACCENT_HOVER = "#e05555"
ACCENT_LIGHT = "#ffe5e5"
ACCENT_DARK  = "#5a2020"
SUCCESS      = "#4CAF50"
ERROR        = "#ef5350"
WARNING      = "#FFA726"
CARD_DARK    = "#2b2b3b"
CARD_LIGHT   = "#fff0f0"

AUTHOR_URL = "https://kevinhaji.com"
REPO_URL   = "https://github.com/kamalalhagh/ClipPress"

# ── Platform-aware data / config directories ──────────────────────────────────
if _WIN:
    _data_home = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    _cfg_home  = _data_home
elif _MAC:
    _data_home = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    _cfg_home  = _data_home
else:
    _data_home = os.environ.get("XDG_DATA_HOME",  os.path.join(os.path.expanduser("~"), ".local", "share"))
    _cfg_home  = os.environ.get("XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config"))

# ── FFmpeg paths ──────────────────────────────────────────────────────────────
FFMPEG_INSTALL_DIR = os.path.join(_data_home, "SoundPress", "ffmpeg")
FFMPEG_EXE         = os.path.join(FFMPEG_INSTALL_DIR, _EXE)

def _ffmpeg_download_url() -> str:
    import platform as _plat
    if _WIN:
        return "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    if _plat.machine() in ("arm64", "aarch64"):
        return "https://evermeet.cx/ffmpeg/getrelease/arm64/ffmpeg/zip"
    return "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"

FFMPEG_DOWNLOAD_URL = _ffmpeg_download_url()

# ── Config ────────────────────────────────────────────────────────────────────
CONFIG_DIR  = os.path.join(_cfg_home, "ClipPress")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def _load_config() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_config(data: dict):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


def walkthrough_should_show() -> bool:
    return not _load_config().get("walkthrough_done", False)


def walkthrough_mark_done():
    cfg = _load_config()
    cfg["walkthrough_done"] = True
    _save_config(cfg)

# ── Translations ──────────────────────────────────────────────────────────────
T = {
    "en": {
        "window_title":  "ClipPress — Video Compressor",
        "title":         "ClipPress",
        "subtitle":      "Video Compressor",
        "import_btn":    "📂  Choose Video File",
        "no_file":       "No file selected — click above to browse",
        "supported":     "Supports: MP4 · MOV · MKV · AVI · WMV · WEBM · FLV · M4V · TS",
        "comp_label":    "Compression Level",
        "c_high_title":  "Maximum",
        "c_high_body":   "720p · CRF 28\nSlowest encode\nSmallest file",
        "c_med_title":   "Medium",
        "c_med_body":    "1080p · CRF 23\nBalanced speed\nGood quality",
        "c_low_title":   "Low",
        "c_low_body":    "1080p · CRF 18\nFast encode\nBest quality",
        "desc_high":     "Best for sharing — smallest file size, 720p output.",
        "desc_med":      "Great balance of quality and file size at 1080p.",
        "desc_low":      "Near-original quality at 1080p — ideal for archiving.",
        "convert_btn":   "⚡  Convert & Save",
        "converting":    "Converting…",
        "status_ready":  "Ready",
        "status_done":   "✅  Saved successfully!",
        "status_err":    "❌  Conversion failed",
        "no_input":      "Please select a video file first.",
        "save_title":    "Save MP4 file",
        "lang_btn":      "فارسی",
        "footer":        "ClipPress v1.0  ·  Powered by FFmpeg",
        "badge_check":   "⚙️ Checking FFmpeg…",
        "badge_ready":   "✅ FFmpeg ready",
        "badge_missing": "⚠️ FFmpeg missing",
        "badge_install": "⚙️ Installing FFmpeg…",
        # installer
        "inst_title":    "FFmpeg Required",
        "inst_msg":      (
            "ClipPress needs FFmpeg to convert video.\n\n"
            "FFmpeg was not found on your system.\n"
            "Click below to download and install it automatically\n"
            "(~80 MB · no admin rights required)."
        ),
        "inst_btn":      "⬇️  Install Automatically",
        "inst_skip":     "Skip",
        "inst_dl":       "Downloading FFmpeg…",
        "inst_extract":  "Extracting files…",
        "inst_path":     "Updating PATH…",
        "inst_done":     "✅  FFmpeg installed successfully!",
        "inst_err":      "❌  Installation failed. Please install manually.",
        "inst_manual":   "Open ffmpeg.org",
        "inst_hint":     "Please wait, this may take a minute…",
        "inst_ok":       "Start ClipPress",
        # about
        "about_title":   "About ClipPress",
        "about_body":    (
            "ClipPress v1.0\n"
            "Video Compressor for Windows\n\n"
            "Developed by  Kevin Haji\n"
            "kevinhaji.com  ·  github.com/kamalalhagh\n\n"
            "Powered by FFmpeg · Built with Python & CustomTkinter\n"
            "github.com/kamalalhagh/ClipPress"
        ),
        "about_btn":     "View on GitHub",
        "about_ok":      "Close",
        # walkthrough
        "wt_title":      "Welcome to ClipPress",
        "wt_skip":       "Skip",
        "wt_next":       "Next  →",
        "wt_done":       "Let's Go  🚀",
        "wt_no_show":    "Don't show again",
        "wt_steps": [
            ("🎬", "Welcome to ClipPress",
             "ClipPress compresses any video file into a\n"
             "compact, high-quality MP4 — perfect for sharing.\n\n"
             "Developed by Kevin Haji\n"
             "github.com/kamalalhagh/ClipPress"),
            ("📂", "Step 1 — Import Video",
             "Click  📂 Choose Video File  to open\n"
             "any video from your computer.\n\n"
             "Supported: MP4 · MOV · MKV · AVI · WMV\n"
             "WEBM · FLV · M4V · TS and more"),
            ("🎚️", "Step 2 — Choose Compression",
             "Pick one of the three compression levels:\n\n"
             "🔥 Maximum  →  720p, smallest file size\n"
             "⚖️ Medium   →  1080p, balanced quality\n"
             "🎵 Low      →  1080p, near-original quality"),
            ("⚡", "Step 3 — Convert & Save",
             "Click  ⚡ Convert & Save  and choose\n"
             "where to save your compressed MP4.\n\n"
             "A progress bar shows real-time % while\n"
             "FFmpeg processes your video."),
        ],
    },
    "fa": {
        "window_title":  "کلیپ‌پرس — فشرده‌ساز ویدیو",
        "title":         "کلیپ‌پرس",
        "subtitle":      "فشرده‌ساز فایل ویدیویی",
        "import_btn":    "📂  انتخاب فایل ویدیویی",
        "no_file":       "فایلی انتخاب نشده — برای مرور کلیک کنید",
        "supported":     "پشتیبانی از: MP4 · MOV · MKV · AVI · WMV · WEBM · FLV · M4V · TS",
        "comp_label":    "سطح فشرده‌سازی",
        "c_high_title":  "حداکثر",
        "c_high_body":   "720p · CRF 28\nکندترین رمزگذاری\nکوچک‌ترین حجم",
        "c_med_title":   "متوسط",
        "c_med_body":    "1080p · CRF 23\nسرعت متعادل\nکیفیت خوب",
        "c_low_title":   "کم",
        "c_low_body":    "1080p · CRF 18\nرمزگذاری سریع\nبهترین کیفیت",
        "desc_high":     "مناسب اشتراک‌گذاری — کمترین حجم، خروجی ۷۲۰p.",
        "desc_med":      "تعادل عالی بین کیفیت و حجم فایل در ۱۰۸۰p.",
        "desc_low":      "کیفیت نزدیک به اصل در ۱۰۸۰p — مناسب آرشیو.",
        "convert_btn":   "⚡  تبدیل و ذخیره",
        "converting":    "در حال تبدیل…",
        "status_ready":  "آماده",
        "status_done":   "✅  با موفقیت ذخیره شد!",
        "status_err":    "❌  تبدیل ناموفق",
        "no_input":      "لطفاً ابتدا یک فایل ویدیویی انتخاب کنید.",
        "save_title":    "ذخیره فایل MP4",
        "lang_btn":      "English",
        "footer":        "کلیپ‌پرس نسخه ۱.۰  ·  مبتنی بر FFmpeg",
        "badge_check":   "⚙️ بررسی FFmpeg…",
        "badge_ready":   "✅ FFmpeg آماده است",
        "badge_missing": "⚠️ FFmpeg پیدا نشد",
        "badge_install": "⚙️ در حال نصب FFmpeg…",
        # installer
        "inst_title":    "FFmpeg لازم است",
        "inst_msg":      (
            "کلیپ‌پرس برای تبدیل ویدیو به FFmpeg نیاز دارد.\n\n"
            "FFmpeg روی سیستم شما پیدا نشد.\n"
            "برای دانلود و نصب خودکار روی دکمه کلیک کنید\n"
            "(حدود ۸۰ مگابایت · بدون نیاز به دسترسی ادمین)."
        ),
        "inst_btn":      "⬇️  نصب خودکار",
        "inst_skip":     "رد کردن",
        "inst_dl":       "در حال دانلود FFmpeg…",
        "inst_extract":  "در حال استخراج فایل‌ها…",
        "inst_path":     "در حال به‌روزرسانی PATH…",
        "inst_done":     "✅  FFmpeg با موفقیت نصب شد!",
        "inst_err":      "❌  نصب ناموفق بود. لطفاً دستی نصب کنید.",
        "inst_manual":   "باز کردن ffmpeg.org",
        "inst_hint":     "لطفاً صبر کنید، ممکن است یک دقیقه طول بکشد…",
        "inst_ok":       "شروع کلیپ‌پرس",
        # about
        "about_title":   "درباره کلیپ‌پرس",
        "about_body":    (
            "کلیپ‌پرس نسخه ۱.۰\n"
            "فشرده‌ساز ویدیو برای ویندوز\n\n"
            "توسعه‌دهنده:  Kevin Haji\n"
            "kevinhaji.com  ·  github.com/kamalalhagh\n\n"
            "مبتنی بر FFmpeg · ساخته شده با Python و CustomTkinter\n"
            "github.com/kamalalhagh/ClipPress"
        ),
        "about_btn":     "مشاهده در GitHub",
        "about_ok":      "بستن",
        # walkthrough
        "wt_title":      "خوش آمدید به کلیپ‌پرس",
        "wt_skip":       "رد کردن",
        "wt_next":       "→  بعدی",
        "wt_done":       "بزن بریم  🚀",
        "wt_no_show":    "دیگر نشان نده",
        "wt_steps": [
            ("🎬", "خوش آمدید به کلیپ‌پرس",
             "کلیپ‌پرس هر فایل ویدیویی را به یک MP4 فشرده\n"
             "و با کیفیت تبدیل می‌کند — مناسب اشتراک‌گذاری.\n\n"
             "توسعه‌دهنده: Kevin Haji\n"
             "github.com/kamalalhagh/ClipPress"),
            ("📂", "مرحله ۱ — انتخاب ویدیو",
             "روی  📂 انتخاب فایل ویدیویی  کلیک کنید\n"
             "تا هر ویدیویی را از کامپیوتر خود باز کنید.\n\n"
             "پشتیبانی از: MP4 · MOV · MKV · AVI · WMV\n"
             "WEBM · FLV · M4V · TS و بیشتر"),
            ("🎚️", "مرحله ۲ — انتخاب فشرده‌سازی",
             "یکی از سه سطح فشرده‌سازی را انتخاب کنید:\n\n"
             "🔥 حداکثر  →  720p، کمترین حجم\n"
             "⚖️ متوسط   →  1080p، کیفیت متعادل\n"
             "🎵 کم       →  1080p، کیفیت نزدیک به اصل"),
            ("⚡", "مرحله ۳ — تبدیل و ذخیره",
             "روی  ⚡ تبدیل و ذخیره  کلیک کنید و محل\n"
             "ذخیره MP4 فشرده‌شده را انتخاب کنید.\n\n"
             "نوار پیشرفت درصد واقعی پردازش FFmpeg\n"
             "را به صورت زنده نمایش می‌دهد."),
        ],
    },
}

_preprocess_fa()

PRESETS = {
    "high":   ["-vf", "scale=-2:720",  "-c:v", "libx264", "-crf", "28", "-preset", "slow",   "-c:a", "aac", "-b:a", "128k"],
    "medium": ["-vf", "scale=-2:1080", "-c:v", "libx264", "-crf", "23", "-preset", "medium", "-c:a", "aac", "-b:a", "192k"],
    "low":    ["-vf", "scale=-2:1080", "-c:v", "libx264", "-crf", "18", "-preset", "fast",   "-c:a", "aac", "-b:a", "256k"],
}

COMP_KEYS  = ["high", "medium", "low"]
COMP_ICONS = {"high": "🔥", "medium": "⚖️", "low": "🎵"}
KEY_MAP    = {"high": "high", "medium": "med", "low": "low"}


# ── FFmpeg helpers ────────────────────────────────────────────────────────────

def _ffmpeg_in_path() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _ffmpeg_local() -> bool:
    return os.path.isfile(FFMPEG_EXE)


def ffmpeg_available() -> bool:
    if getattr(sys, "frozen", False):
        bundled = os.path.join(sys._MEIPASS, _EXE)
        if os.path.isfile(bundled):
            return True
    return _ffmpeg_in_path() or _ffmpeg_local()


def ffmpeg_cmd() -> str:
    """Return path to ffmpeg — bundled binary takes priority."""
    # 1. Check for binary bundled inside the PyInstaller EXE
    if getattr(sys, "frozen", False):
        bundled = os.path.join(sys._MEIPASS, _EXE)
        if os.path.isfile(bundled):
            return bundled
    # 2. System PATH
    if _ffmpeg_in_path():
        return "ffmpeg"
    # 3. Previously auto-installed locally
    if _ffmpeg_local():
        return FFMPEG_EXE
    return "ffmpeg"


def _get_duration(filepath: str, exe: str) -> float:
    try:
        result = subprocess.run(
            [exe, "-i", filepath],
            capture_output=True, text=True, errors="ignore"
        )
        m = re.search(r"Duration: (\d+):(\d+):(\d+)\.(\d+)", result.stderr)
        if m:
            h, mi, s, cs = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
            return h * 3600 + mi * 60 + s + cs / 100
    except Exception:
        pass
    return 0


def _add_to_user_path(new_dir: str):
    if sys.platform != "win32":
        return
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS)
        try:
            current, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current = ""
        if new_dir.lower() not in current.lower():
            updated = (current.rstrip(";") + ";" + new_dir) if current else new_dir
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, updated)
        winreg.CloseKey(key)
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 2, 5000, None)
    except Exception:
        pass
    os.environ["PATH"] = new_dir + os.pathsep + os.environ.get("PATH", "")


# ── FFmpeg Installer Dialog ───────────────────────────────────────────────────

class FFmpegInstallerDialog(ctk.CTkToplevel):
    def __init__(self, parent, lang: str, on_done_cb):
        super().__init__(parent)
        self.lang       = lang
        self.on_done_cb = on_done_cb
        t = T[lang]
        self.title(t["inst_title"])
        self.geometry("450x370")
        self.resizable(False, False)
        self.grab_set()
        self.lift()
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", self._skip)
        px = parent.winfo_x() + (parent.winfo_width()  - 450) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 370) // 2
        self.geometry(f"450x370+{px}+{py}")
        self._build(t)

    def _build(self, t):
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="🎬", font=ctk.CTkFont(size=44)).grid(row=0, column=0, pady=(26, 2))
        ctk.CTkLabel(self, text=t["inst_title"], font=ctk.CTkFont(size=18, weight="bold")).grid(row=1, column=0, pady=(0, 4))
        self.lbl_msg = ctk.CTkLabel(self, text=t["inst_msg"], font=ctk.CTkFont(size=12),
                                    text_color=("gray30", "gray70"), justify="center", wraplength=390)
        self.lbl_msg.grid(row=2, column=0, padx=24, pady=(0, 14))
        self.progress = ctk.CTkProgressBar(self, height=6, corner_radius=3)
        self.progress.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 4))
        self.progress.set(0)
        self.progress.grid_remove()
        self.lbl_status = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11),
                                       text_color=("gray45", "gray60"))
        self.lbl_status.grid(row=4, column=0, pady=(0, 14))
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=5, column=0, pady=(0, 22))
        self.btn_install = ctk.CTkButton(btn_row, text=t["inst_btn"], width=210, height=44,
                                         font=ctk.CTkFont(size=13, weight="bold"),
                                         fg_color=ACCENT, hover_color=ACCENT_HOVER, command=self._start_install)
        self.btn_install.pack(side="left", padx=6)
        self.btn_skip = ctk.CTkButton(btn_row, text=t["inst_skip"], width=90, height=44,
                                      fg_color=("gray85","gray25"), hover_color=("gray75","gray35"),
                                      text_color=("gray10","white"),
                                      font=ctk.CTkFont(size=12), command=self._skip)
        self.btn_skip.pack(side="left", padx=6)

    def _status(self, text, color=("gray45", "gray60")):
        self.lbl_status.configure(text=text, text_color=color)
        self.update_idletasks()

    def _start_install(self):
        t = T[self.lang]
        self.btn_install.configure(state="disabled")
        self.btn_skip.configure(state="disabled")
        self.progress.grid()
        self.progress.configure(mode="indeterminate")
        self.progress.start()
        self._status(t["inst_hint"])
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        t = T[self.lang]
        tmpzip = None
        try:
            self.after(0, self._status, t["inst_dl"])
            os.makedirs(FFMPEG_INSTALL_DIR, exist_ok=True)
            fd, tmpzip = tempfile.mkstemp(suffix=".zip", prefix="ffmpeg_dl_")
            os.close(fd)
            switched = [False]
            def reporthook(block, bsize, total):
                if total > 0:
                    if not switched[0]:
                        switched[0] = True
                        self.after(0, lambda: self.progress.stop())
                        self.after(0, lambda: self.progress.configure(mode="determinate"))
                    pct = min(block * bsize / total, 1.0)
                    mb_done  = min(block * bsize, total) // (1024 * 1024)
                    mb_total = total // (1024 * 1024)
                    self.after(0, self.progress.set, pct)
                    self.after(0, self._status, f"{t['inst_dl']}  {mb_done} / {mb_total} MB")
            urllib.request.urlretrieve(FFMPEG_DOWNLOAD_URL, tmpzip, reporthook)
            self.after(0, self._status, t["inst_extract"])
            self.after(0, lambda: self.progress.configure(mode="indeterminate"))
            self.after(0, lambda: self.progress.start())
            with zipfile.ZipFile(tmpzip, "r") as zf:
                if _WIN:
                    entry = next((n for n in zf.namelist()
                                  if n.endswith("/bin/ffmpeg.exe") or n == "bin/ffmpeg.exe"), None)
                else:
                    # evermeet.cx: binary sits at the root of the zip
                    entry = next((n for n in zf.namelist()
                                  if n == "ffmpeg" or n.endswith("/ffmpeg")), None)
                if not entry:
                    raise FileNotFoundError(f"{_EXE} not found in archive")
                with zf.open(entry) as src, open(FFMPEG_EXE, "wb") as dst:
                    shutil.copyfileobj(src, dst)
            if not _WIN:
                import stat as _stat
                os.chmod(FFMPEG_EXE, os.stat(FFMPEG_EXE).st_mode | _stat.S_IXUSR | _stat.S_IXGRP | _stat.S_IXOTH)
            self.after(0, self._status, t["inst_path"])
            _add_to_user_path(FFMPEG_INSTALL_DIR)
            self.after(0, self._on_success)
        except Exception:
            self.after(0, self._on_error)
        finally:
            if tmpzip and os.path.exists(tmpzip):
                try:
                    os.remove(tmpzip)
                except Exception:
                    pass

    def _on_success(self):
        t = T[self.lang]
        self.progress.stop()
        self.progress.configure(mode="determinate")
        self.progress.set(1.0)
        self._status(t["inst_done"], SUCCESS)
        self.btn_install.configure(state="normal", text=t["inst_ok"],
                                   fg_color=SUCCESS, hover_color="#43a047", command=self._finish_ok)
        self.btn_skip.configure(state="disabled")

    def _on_error(self):
        t = T[self.lang]
        self.progress.stop()
        self.progress.configure(mode="determinate")
        self.progress.set(0)
        self._status(t["inst_err"], ERROR)
        self.btn_install.configure(state="normal", text=t["inst_manual"],
                                   fg_color=ERROR, hover_color="#e53935",
                                   command=lambda: webbrowser.open("https://ffmpeg.org/download.html"))
        self.btn_skip.configure(state="normal")
        self.on_done_cb(False)

    def _finish_ok(self):
        self.destroy()
        self.on_done_cb(True)

    def _skip(self):
        self.destroy()
        self.on_done_cb(False)


# ── Walkthrough Dialog ────────────────────────────────────────────────────────

class WalkthroughDialog(ctk.CTkToplevel):
    def __init__(self, parent, lang: str, on_close_cb=None):
        super().__init__(parent)
        self.lang        = lang
        self.on_close_cb = on_close_cb
        self._step       = 0
        t                = T[lang]
        self._steps      = t["wt_steps"]
        self.title(t["wt_title"])
        self.geometry("480x400")
        self.resizable(False, False)
        self.grab_set()
        self.lift()
        self.focus_force()
        self.protocol("WM_DELETE_WINDOW", self._close)
        px = parent.winfo_x() + (parent.winfo_width()  - 480) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 400) // 2
        self.geometry(f"480x400+{px}+{py}")
        self._build()
        self._render_step()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.lbl_icon = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=46))
        self.lbl_icon.grid(row=0, column=0, pady=(28, 4))
        self.lbl_step_title = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_step_title.grid(row=1, column=0, pady=(0, 4))
        self.lbl_body = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12),
                                     text_color=("gray30", "gray70"), justify="center", wraplength=420)
        self.lbl_body.grid(row=2, column=0, padx=30, pady=(0, 16))
        dot_frame = ctk.CTkFrame(self, fg_color="transparent")
        dot_frame.grid(row=3, column=0, pady=(0, 12))
        self._dots = []
        for i in range(len(self._steps)):
            d = ctk.CTkLabel(dot_frame, text="●", font=ctk.CTkFont(size=10))
            d.pack(side="left", padx=3)
            self._dots.append(d)
        self._no_show_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self, text=T[self.lang]["wt_no_show"], variable=self._no_show_var,
                        font=ctk.CTkFont(size=11), checkbox_width=16, checkbox_height=16).grid(row=4, column=0, pady=(0, 10))
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=5, column=0, pady=(0, 22))
        self.btn_skip = ctk.CTkButton(btn_row, text=T[self.lang]["wt_skip"], width=90, height=38,
                                      fg_color=("gray85","gray25"), hover_color=("gray75","gray35"),
                                      text_color=("gray10","white"),
                                      font=ctk.CTkFont(size=12), command=self._close)
        self.btn_skip.pack(side="left", padx=6)
        self.btn_next = ctk.CTkButton(btn_row, text=T[self.lang]["wt_next"], width=140, height=38,
                                      fg_color=ACCENT, hover_color=ACCENT_HOVER,
                                      font=ctk.CTkFont(size=13, weight="bold"), command=self._next)
        self.btn_next.pack(side="left", padx=6)

    def _render_step(self):
        icon, title, body = self._steps[self._step]
        self.lbl_icon.configure(text=icon)
        self.lbl_step_title.configure(text=title)
        self.lbl_body.configure(text=body)
        last = self._step == len(self._steps) - 1
        self.btn_next.configure(text=T[self.lang]["wt_done"] if last else T[self.lang]["wt_next"])
        for i, d in enumerate(self._dots):
            d.configure(text_color=ACCENT if i == self._step else ("gray60", "gray50"))

    def _next(self):
        if self._step < len(self._steps) - 1:
            self._step += 1
            self._render_step()
        else:
            self._close()

    def _close(self):
        if self._no_show_var.get():
            walkthrough_mark_done()
        self.destroy()
        if self.on_close_cb:
            self.on_close_cb()


# ── About Dialog ──────────────────────────────────────────────────────────────

class AboutDialog(ctk.CTkToplevel):
    def __init__(self, parent, lang: str):
        super().__init__(parent)
        t = T[lang]
        self.title(t["about_title"])
        self.geometry("380x300")
        self.resizable(False, False)
        self.grab_set()
        self.lift()
        self.focus_force()
        px = parent.winfo_x() + (parent.winfo_width()  - 380) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 300) // 2
        self.geometry(f"380x300+{px}+{py}")
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="🎬", font=ctk.CTkFont(size=40)).grid(row=0, column=0, pady=(22, 4))
        ctk.CTkLabel(self, text=t["about_title"], font=ctk.CTkFont(size=17, weight="bold")).grid(row=1, column=0)
        ctk.CTkLabel(self, text=t["about_body"], font=ctk.CTkFont(size=11),
                     text_color=("gray30", "gray70"), justify="center", wraplength=330).grid(row=2, column=0, padx=24, pady=(10, 14))
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=3, column=0, pady=(0, 20))
        ctk.CTkButton(btn_row, text=t["about_btn"], width=160, height=36,
                      fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      font=ctk.CTkFont(size=12),
                      command=lambda: webbrowser.open(REPO_URL)).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text=t["about_ok"], width=80, height=36,
                      fg_color=("gray85","gray25"), hover_color=("gray75","gray35"),
                      text_color=("gray10","white"),
                      font=ctk.CTkFont(size=12), command=self.destroy).pack(side="left", padx=6)


# ── Main App ──────────────────────────────────────────────────────────────────

class ClipPressApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.lang        = "en"
        self.input_file  = None
        self.compression = "high"
        self._is_dark    = True

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(T["en"]["window_title"])
        self.geometry("540x710")
        self.resizable(False, False)

        base      = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(__file__)
        if _WIN:
            icon_path = os.path.join(base, "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)

        self._build_ui()
        self._refresh_all()
        self.after(400, self._startup_ffmpeg_check)

    # ── FFmpeg startup ────────────────────────────────────────────

    def _startup_ffmpeg_check(self):
        if ffmpeg_available():
            self._badge(self.lang, "badge_ready", SUCCESS)
            self._maybe_show_walkthrough()
        else:
            # If bundled EXE but ffmpeg still missing — show badge only, no download
            if getattr(sys, "frozen", False):
                self._badge(self.lang, "badge_missing", ERROR)
                self._maybe_show_walkthrough()
            else:
                self._badge(self.lang, "badge_install", WARNING)
                FFmpegInstallerDialog(self, self.lang, self._on_install_done)

    def _on_install_done(self, ok: bool):
        self._badge(self.lang, "badge_ready" if (ok or ffmpeg_available()) else "badge_missing",
                    SUCCESS if (ok or ffmpeg_available()) else ERROR)
        self._maybe_show_walkthrough()

    def _maybe_show_walkthrough(self):
        if walkthrough_should_show():
            self.after(200, lambda: WalkthroughDialog(self, self.lang))

    def _badge(self, lang, key, color):
        self.lbl_badge.configure(text=T[lang][key], text_color=color)

    # ── Build UI ──────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # Top bar
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 0))
        top.grid_columnconfigure(1, weight=1)
        tf = ctk.CTkFrame(top, fg_color="transparent")
        tf.grid(row=0, column=0, sticky="w")
        self.lbl_title = ctk.CTkLabel(tf, text="", font=ctk.CTkFont(size=30, weight="bold"))
        self.lbl_title.pack(anchor="w")
        self.lbl_subtitle = ctk.CTkLabel(tf, text="", font=ctk.CTkFont(size=13),
                                         text_color=("gray50", "gray60"))
        self.lbl_subtitle.pack(anchor="w")
        br = ctk.CTkFrame(top, fg_color="transparent")
        br.grid(row=0, column=2, sticky="e")
        self.btn_lang = ctk.CTkButton(br, text="", width=72, height=32,
                                      fg_color=("gray85","gray25"), hover_color=("gray75","gray35"),
                                      text_color=("gray10","white"),
                                      font=ctk.CTkFont(size=12), command=self._toggle_lang)
        self.btn_lang.pack(side="left", padx=(0, 6))
        self.btn_theme = ctk.CTkButton(br, text="☀️", width=38, height=32,
                                       fg_color=("gray85","gray25"), hover_color=("gray75","gray35"),
                                       text_color=("gray10","white"),
                                       font=ctk.CTkFont(size=14), command=self._toggle_theme)
        self.btn_theme.pack(side="left")
        ctk.CTkButton(br, text="📖", width=36, height=32,
                      fg_color=("gray85","gray25"), hover_color=("gray75","gray35"),
                      text_color=("gray10","white"),
                      font=ctk.CTkFont(size=13),
                      command=self._show_walkthrough).pack(side="left", padx=(6, 0))
        ctk.CTkButton(br, text="?", width=32, height=32,
                      fg_color=("gray85","gray25"), hover_color=("gray75","gray35"),
                      text_color=("gray10","white"),
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._show_about).pack(side="left", padx=(6, 0))

        # Divider
        ctk.CTkFrame(self, height=1, fg_color=("gray75", "gray30")).grid(
            row=1, column=0, sticky="ew", padx=24, pady=14)

        # File card
        fc = ctk.CTkFrame(self, corner_radius=12)
        fc.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 14))
        fc.grid_columnconfigure(0, weight=1)
        self.btn_import = ctk.CTkButton(fc, text="", height=46,
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        fg_color=ACCENT, hover_color=ACCENT_HOVER,
                                        corner_radius=8, command=self._browse_file)
        self.btn_import.grid(row=0, column=0, padx=16, pady=(16, 8), sticky="ew")
        self.lbl_file = ctk.CTkLabel(fc, text="", font=ctk.CTkFont(size=11),
                                     text_color=("gray50", "gray60"), wraplength=460)
        self.lbl_file.grid(row=1, column=0, padx=16, pady=(0, 4))
        self.lbl_supported = ctk.CTkLabel(fc, text="", font=ctk.CTkFont(size=10),
                                          text_color=("gray55", "gray55"))
        self.lbl_supported.grid(row=2, column=0, padx=16, pady=(0, 12))

        # Compression header
        self.lbl_comp_hdr = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_comp_hdr.grid(row=3, column=0, sticky="w", padx=24, pady=(0, 8))

        # Compression cards
        cf = ctk.CTkFrame(self, fg_color="transparent")
        cf.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 6))
        cf.grid_columnconfigure((0, 1, 2), weight=1)
        self.comp_cards = {}
        self.comp_lbl_title = {}
        self.comp_lbl_body  = {}
        for i, key in enumerate(COMP_KEYS):
            card = ctk.CTkFrame(cf, corner_radius=12, cursor="hand2")
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            ctk.CTkLabel(card, text=COMP_ICONS[key], font=ctk.CTkFont(size=24)).pack(pady=(14, 2))
            tl = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=12, weight="bold"))
            tl.pack()
            bl = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=9),
                              text_color=("gray50", "gray60"), justify="center")
            bl.pack(pady=(2, 14))
            for w in [card] + card.winfo_children():
                w.bind("<Button-1>", lambda e, k=key: self._select_compression(k))
            self.comp_cards[key]     = card
            self.comp_lbl_title[key] = tl
            self.comp_lbl_body[key]  = bl

        # Description
        self.lbl_desc = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11),
                                     text_color=("gray45", "gray60"), wraplength=480)
        self.lbl_desc.grid(row=5, column=0, padx=24, pady=(4, 14))

        # Convert button
        self.btn_convert = ctk.CTkButton(self, text="", height=52,
                                         font=ctk.CTkFont(size=15, weight="bold"),
                                         fg_color=ACCENT, hover_color=ACCENT_HOVER,
                                         corner_radius=12, command=self._start_conversion)
        self.btn_convert.grid(row=6, column=0, sticky="ew", padx=24, pady=(0, 10))

        # Progress bar + percent label
        prog_frame = ctk.CTkFrame(self, fg_color="transparent")
        prog_frame.grid(row=7, column=0, sticky="ew", padx=24, pady=(0, 4))
        prog_frame.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(prog_frame, height=8, corner_radius=4)
        self.progress.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        self.progress.set(0)

        self.lbl_pct = ctk.CTkLabel(prog_frame, text="", font=ctk.CTkFont(size=11),
                                    text_color=("gray50", "gray60"))
        self.lbl_pct.grid(row=1, column=0)

        # Status
        self.lbl_status = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12),
                                       text_color=("gray50", "gray55"))
        self.lbl_status.grid(row=8, column=0, pady=(0, 2))

        # Footer
        ff = ctk.CTkFrame(self, fg_color="transparent")
        ff.grid(row=9, column=0, pady=(2, 4))
        self.lbl_footer = ctk.CTkLabel(ff, text="", font=ctk.CTkFont(size=10),
                                       text_color=("gray55", "gray50"))
        self.lbl_footer.pack(side="left")
        ctk.CTkLabel(ff, text="  ·  ", font=ctk.CTkFont(size=10),
                     text_color=("gray55", "gray50")).pack(side="left")
        lnk = ctk.CTkLabel(ff, text="ffmpeg.org", font=ctk.CTkFont(size=10, underline=True),
                           text_color=ACCENT, cursor="hand2")
        lnk.pack(side="left")
        lnk.bind("<Button-1>", lambda e: webbrowser.open("https://ffmpeg.org/download.html"))
        ctk.CTkLabel(ff, text="  ·  ", font=ctk.CTkFont(size=10),
                     text_color=("gray55", "gray50")).pack(side="left")
        gh = ctk.CTkLabel(ff, text="by Kevin Haji", font=ctk.CTkFont(size=10, underline=True),
                          text_color=ACCENT, cursor="hand2")
        gh.pack(side="left")
        gh.bind("<Button-1>", lambda e: webbrowser.open(AUTHOR_URL))

        # FFmpeg badge
        self.lbl_badge = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=10), text_color=WARNING)
        self.lbl_badge.grid(row=10, column=0, pady=(0, 12))

    # ── Logic ─────────────────────────────────────────────────────

    def _refresh_all(self):
        t = T[self.lang]
        self.title(t["window_title"])
        self.lbl_title.configure(text=t["title"])
        self.lbl_subtitle.configure(text=t["subtitle"])
        self.btn_import.configure(text=t["import_btn"])
        self.lbl_supported.configure(text=t["supported"])
        self.lbl_comp_hdr.configure(text=t["comp_label"])
        self.btn_convert.configure(text=t["convert_btn"])
        self.lbl_footer.configure(text=t["footer"])
        self.btn_lang.configure(text=t["lang_btn"])
        self.lbl_badge.configure(text=t["badge_check"])
        if not self.input_file:
            self.lbl_file.configure(text=t["no_file"], text_color=("gray50", "gray60"))
        self.lbl_status.configure(text=t["status_ready"])
        for key in COMP_KEYS:
            k = KEY_MAP[key]
            self.comp_lbl_title[key].configure(text=t[f"c_{k}_title"])
            self.comp_lbl_body[key].configure(text=t[f"c_{k}_body"])
        self._update_card_visuals()
        self._update_desc()

    def _update_card_visuals(self):
        for key, card in self.comp_cards.items():
            if key == self.compression:
                card.configure(fg_color=(CARD_LIGHT, CARD_DARK), border_width=2, border_color=ACCENT)
            else:
                card.configure(fg_color=("gray90", "gray20"), border_width=0)

    def _update_desc(self):
        self.lbl_desc.configure(text=T[self.lang][f"desc_{KEY_MAP[self.compression]}"])

    def _select_compression(self, key):
        self.compression = key
        self._update_card_visuals()
        self._update_desc()

    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.mov *.mkv *.avi *.wmv *.webm *.flv *.m4v *.ts *.3gp *.mpeg"),
                       ("All Files", "*.*")]
        )
        if path:
            self.input_file = path
            name = os.path.basename(path)
            size = os.path.getsize(path) / (1024 * 1024)
            self.lbl_file.configure(text=f"🎬  {name}  ({size:.1f} MB)",
                                    text_color=("gray20", "white"))
            self.progress.set(0)
            self.lbl_pct.configure(text="")
            self.lbl_status.configure(text=T[self.lang]["status_ready"],
                                      text_color=("gray50", "gray55"))

    def _toggle_lang(self):
        self.lang = "fa" if self.lang == "en" else "en"
        self._refresh_all()

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        ctk.set_appearance_mode("dark" if self._is_dark else "light")
        self.btn_theme.configure(text="☀️" if self._is_dark else "🌙")

    def _show_about(self):
        AboutDialog(self, self.lang)

    def _show_walkthrough(self):
        WalkthroughDialog(self, self.lang)

    def _start_conversion(self):
        t = T[self.lang]
        if not self.input_file:
            messagebox.showwarning("ClipPress", t["no_input"])
            return
        if not ffmpeg_available():
            self._startup_ffmpeg_check()
            return
        base = os.path.splitext(os.path.basename(self.input_file))[0]
        out  = filedialog.asksaveasfilename(
            title=t["save_title"], defaultextension=".mp4",
            initialfile=base + "_compressed.mp4",
            filetypes=[("MP4 Video", "*.mp4")]
        )
        if not out:
            return
        self.btn_convert.configure(state="disabled", text=t["converting"])
        self.lbl_status.configure(text=t["converting"], text_color=("gray50", "gray55"))
        self.progress.configure(mode="indeterminate")
        self.progress.start()
        self.lbl_pct.configure(text="")
        threading.Thread(target=self._run_ffmpeg, args=(out,), daemon=True).start()

    def _run_ffmpeg(self, out_path):
        exe      = ffmpeg_cmd()
        duration = _get_duration(self.input_file, exe)
        # -progress and -nostats are global options — must come before -i
        cmd = [exe, "-y", "-progress", "pipe:1", "-nostats",
               "-i", self.input_file] + PRESETS[self.compression] + [out_path]
        ok = False
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0
            )
            # Drain stderr in background thread to prevent buffer deadlock
            threading.Thread(target=lambda: proc.stderr.read(), daemon=True).start()
            while True:
                raw = proc.stdout.readline()
                if not raw:
                    break
                line = raw.decode(errors="ignore").strip()
                if line.startswith("out_time_ms="):
                    try:
                        ms  = int(line.split("=")[1])
                        if ms > 0 and duration > 0:
                            pct = min(ms / 1_000_000 / duration, 0.99)
                            self.after(0, self._update_progress, pct)
                    except ValueError:
                        pass
            proc.wait()
            ok = proc.returncode == 0
        except Exception:
            ok = False
        self.after(0, self._on_done, ok, out_path)

    def _update_progress(self, pct: float):
        self.progress.configure(mode="determinate")
        self.progress.set(pct)
        self.lbl_pct.configure(text=f"{pct * 100:.0f}%")
        self.lbl_status.configure(
            text=f"{T[self.lang]['converting']}  {pct * 100:.0f}%",
            text_color=("gray50", "gray55")
        )

    def _on_done(self, ok: bool, out_path: str):
        self.progress.stop()
        self.progress.configure(mode="determinate")
        self.progress.set(1.0 if ok else 0.0)
        t = T[self.lang]
        if ok:
            orig_mb = os.path.getsize(self.input_file) / (1024 * 1024)
            new_mb  = os.path.getsize(out_path)        / (1024 * 1024)
            saved   = (1 - new_mb / orig_mb) * 100 if orig_mb else 0
            self.lbl_pct.configure(text="100%")
            self.lbl_status.configure(
                text=f"{t['status_done']}  {new_mb:.1f} MB  (saved {saved:.0f}%)",
                text_color=SUCCESS)
        else:
            self.lbl_pct.configure(text="")
            self.lbl_status.configure(text=t["status_err"], text_color=ERROR)
        self.btn_convert.configure(state="normal", text=t["convert_btn"])


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = ClipPressApp()
    app.mainloop()
