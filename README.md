# Browser Logger

[![Release](https://img.shields.io/github/v/release/rezaldi212/browserlogger)](https://github.com/rezaldi212/browserlogger/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

A lightweight Qt browser with a live logging panel. It captures page text and user-selected text while browsing.

## Overview

Browser Logger is a small desktop app for browsing pages while recording page text, navigation events, and highlighted selections into session logs.

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
