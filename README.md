# Browser Logger

A lightweight Qt browser with a live logging panel. It captures page text and user-selected text while browsing.

## Install

```bash
pip install -r requirements.txt
```

## Jalankan

```bash
python browser_logger.py
```

## Features

- Top section: address bar, back/forward/reload, and browser view (`QWebEngineView`, Chromium)
- Bottom section: real-time log panel with resizable splitter
- Otomatis capture:
  - `[NAV]` perubahan URL
  - `[LOAD]` status load halaman
  - `[PAGE]` seluruh visible text saat halaman selesai load
  - `[SELECT]` teks yang user highlight
- Auto-save to `logs/session_YYYYMMDD_HHMMSS.log`
- Buttons: **Capture Page Text Now**, **Clear**, **Save As...**

## License

MIT
