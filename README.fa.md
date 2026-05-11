# کلیپ‌پرس — فشرده‌ساز ویدیو

<p align="center">
  <img src="https://img.shields.io/github/v/release/kamalalhagh/ClipPress?style=flat-square&color=FF6B6B" alt="نسخه">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS-blue?style=flat-square" alt="پلتفرم">
  <img src="https://img.shields.io/badge/python-3.12-brightgreen?style=flat-square" alt="پایتون">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="مجوز">
</p>

یک اپلیکیشن دسکتاپ دوزبانه (فارسی / انگلیسی) برای فشرده‌سازی هر ویدیویی به MP4 با استفاده از FFmpeg. سه پیش‌تنظیم آماده برای هر کاربردی — بدون نیاز به خط فرمان یا تنظیمات اولیه.

**[دانلود آخرین نسخه](https://github.com/kamalalhagh/ClipPress/releases/latest)** | **[English README](README.md)**

---

## ویژگی‌ها

- سه سطح فشرده‌سازی — حداکثر (۷۲۰p)، متوسط (۱۰۸۰p)، کم (۱۰۸۰p با کیفیت بالا)
- رابط کاربری فارسی / انگلیسی با نمایش صحیح RTL
- تم تاریک و روشن
- FFmpeg در فایل دانلودی جاسازی شده — بدون نیاز به هیچ تنظیمی
- نوار پیشرفت زنده با نمایش درصد واقعی در حین تبدیل
- پشتیبانی از MP4، MOV، MKV، AVI، WMV، WEBM، FLV، M4V، TS و بیشتر

---

## دانلود

| پلتفرم | فایل |
|--------|------|
| ویندوز Intel / AMD | `ClipPress-windows-x64.exe` |
| ویندوز ARM64 | `ClipPress-windows-arm64.exe` |
| macOS Universal (پیشنهادی) | `ClipPress-macOS-universal` |
| macOS Apple Silicon | `ClipPress-macOS-arm64` |
| macOS Intel | `ClipPress-macOS-intel` |

در macOS، یک بار پس از دانلود این دستور را اجرا کنید:

```bash
chmod +x ClipPress-macOS-*
xattr -d com.apple.quarantine ClipPress-macOS-*
```

---

## پیش‌تنظیم‌های فشرده‌سازی

| سطح | رزولوشن | CRF | Preset | صدا | مناسب برای |
|-----|---------|-----|--------|-----|------------|
| حداکثر | ۷۲۰p | ۲۸ | slow | AAC 128k | اشتراک‌گذاری |
| متوسط | ۱۰۸۰p | ۲۳ | medium | AAC 192k | استفاده عمومی |
| کم | ۱۰۸۰p | ۱۸ | fast | AAC 256k | آرشیو |

---

## اجرا از سورس‌کد

```bash
git clone https://github.com/kamalalhagh/ClipPress.git
cd ClipPress
pip install -r requirements.txt
python main.py
```

نیاز به Python نسخه ۳.۹ یا بالاتر دارد. FFmpeg باید در PATH باشد، یا برنامه در اولین اجرا نصب آن را پیشنهاد می‌دهد.

---

## نویسنده

**Kevin Haji** — [kevinhaji.com](https://kevinhaji.com) · [github.com/kamalalhagh](https://github.com/kamalalhagh)

---

## مجوز

MIT © [Kevin Haji](https://kevinhaji.com)
