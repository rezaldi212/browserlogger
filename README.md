# Browser Logger

GUI browser dengan panel logger di bawah. Merekam teks halaman + teks yang di-select user.

## Install

```bash
pip install -r requirements.txt
```

## Jalankan

```bash
python browser_logger.py
```

## Fitur

- **Atas**: address bar + back/forward/reload + browser (QWebEngineView, Chromium)
- **Bawah**: panel log real-time, dapat di-resize via splitter
- Otomatis capture:
  - `[NAV]` perubahan URL
  - `[LOAD]` status load halaman
  - `[PAGE]` seluruh visible text saat halaman selesai load
  - `[SELECT]` teks yang user highlight
- Auto-save ke `logs/session_YYYYMMDD_HHMMSS.log`
- Tombol **Capture Page Text Now**, **Clear**, **Save As...**
