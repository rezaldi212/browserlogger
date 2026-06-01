import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QUrl, Qt, Slot, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWebEngineWidgets import QWebEngineView


LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


class BrowserLogger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Browser Logger")
        self.resize(1200, 900)

        session_name = datetime.now().strftime("session_%Y%m%d_%H%M%S.log")
        self.log_file_path = LOG_DIR / session_name
        self.log_fp = open(self.log_file_path, "a", encoding="utf-8")

        self._seen_lines: set[str] = set()
        self._last_selection = ""
        self._current_url = ""

        self._build_ui()
        self._wire_signals()

        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._capture_page_text)
        self.poll_timer.start(self.interval_spin.value() * 1000)

        self.browser.setUrl(QUrl("https://www.google.com"))
        self._log("SYSTEM", f"Log file: {self.log_file_path}")

    def _build_ui(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.back_btn = QPushButton("←")
        self.fwd_btn = QPushButton("→")
        self.reload_btn = QPushButton("⟳")
        for b in (self.back_btn, self.fwd_btn, self.reload_btn):
            b.setFixedWidth(36)
            toolbar.addWidget(b)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL and press Enter...")
        toolbar.addWidget(self.url_bar)

        self.go_btn = QPushButton("Go")
        toolbar.addWidget(self.go_btn)

        self.browser = QWebEngineView()

        log_container = QWidget()
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(4, 4, 4, 4)

        self.log_label = QLabel(f"Logger → {self.log_file_path.name}")
        self.log_label.setStyleSheet("font-weight: bold;")
        log_layout.addWidget(self.log_label)

        btn_row = QWidget()
        h = QHBoxLayout(btn_row)
        h.setContentsMargins(0, 0, 0, 0)

        self.auto_chk = QCheckBox("Auto-capture")
        self.auto_chk.setChecked(True)

        h.addWidget(self.auto_chk)
        h.addWidget(QLabel("every"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(2)
        self.interval_spin.setSuffix(" s")
        h.addWidget(self.interval_spin)

        self.capture_btn = QPushButton("Capture Now")
        self.clear_btn = QPushButton("Clear")
        self.save_as_btn = QPushButton("Save As...")
        h.addWidget(self.capture_btn)
        h.addWidget(self.clear_btn)
        h.addWidget(self.save_as_btn)
        h.addStretch()
        log_layout.addWidget(btn_row)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet(
            "background-color: #1e1e1e; color: #d4d4d4; "
            "font-family: Consolas, monospace; font-size: 11pt;"
        )
        log_layout.addWidget(self.log_view)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.browser)
        splitter.addWidget(log_container)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([550, 350])

        self.setCentralWidget(splitter)

    def _wire_signals(self):
        self.url_bar.returnPressed.connect(self._navigate_from_bar)
        self.go_btn.clicked.connect(self._navigate_from_bar)
        self.back_btn.clicked.connect(self.browser.back)
        self.fwd_btn.clicked.connect(self.browser.forward)
        self.reload_btn.clicked.connect(self.browser.reload)

        self.browser.urlChanged.connect(self._on_url_changed)
        self.browser.loadFinished.connect(self._on_load_finished)
        self.browser.page().selectionChanged.connect(self._on_selection_changed)

        self.clear_btn.clicked.connect(self.log_view.clear)
        self.save_as_btn.clicked.connect(self._save_as)
        self.capture_btn.clicked.connect(self._capture_page_text)
        self.auto_chk.toggled.connect(self._on_auto_toggled)
        self.interval_spin.valueChanged.connect(self._on_interval_changed)

    @Slot()
    def _navigate_from_bar(self):
        text = self.url_bar.text().strip()
        if not text:
            return
        if "://" not in text and not text.startswith("about:"):
            if "." in text and " " not in text:
                text = "https://" + text
            else:
                text = f"https://www.google.com/search?q={QUrl.toPercentEncoding(text).data().decode()}"
        self.browser.setUrl(QUrl(text))

    @Slot(QUrl)
    def _on_url_changed(self, url: QUrl):
        url_str = url.toString()
        self.url_bar.setText(url_str)
        if url_str != self._current_url:
            self._current_url = url_str
            self._seen_lines.clear()
            self._log("NAV", url_str)

    @Slot(bool)
    def _on_load_finished(self, ok: bool):
        self._log("LOAD", "OK" if ok else "FAILED")
        if ok:
            self._capture_page_text()

    @Slot(bool)
    def _on_auto_toggled(self, checked: bool):
        if checked:
            self.poll_timer.start(self.interval_spin.value() * 1000)
            self._log("SYSTEM", f"Auto-capture ON ({self.interval_spin.value()}s)")
        else:
            self.poll_timer.stop()
            self._log("SYSTEM", "Auto-capture OFF")

    @Slot(int)
    def _on_interval_changed(self, value: int):
        if self.auto_chk.isChecked():
            self.poll_timer.start(value * 1000)

    @Slot()
    def _capture_page_text(self):
        self.browser.page().runJavaScript(
            "document.body ? document.body.innerText : ''",
            self._on_page_text,
        )

    def _on_page_text(self, text):
        if not text:
            return
        new_lines = []
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line in self._seen_lines:
                continue
            self._seen_lines.add(line)
            new_lines.append(line)
        if not new_lines:
            return
        self._log("PAGE", "\n".join(new_lines))

    @Slot()
    def _on_selection_changed(self):
        selected = self.browser.page().selectedText().strip()
        if not selected or selected == self._last_selection:
            return
        self._last_selection = selected
        self._log("SELECT", selected)

    def _log(self, tag: str, message: str):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] [{tag}] {message}"
        self.log_view.appendPlainText(line)
        self.log_view.moveCursor(QTextCursor.End)
        try:
            self.log_fp.write(line + "\n")
            self.log_fp.flush()
        except Exception:
            pass

    @Slot()
    def _save_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Log As", str(self.log_file_path), "Log Files (*.log *.txt)"
        )
        if not path:
            return
        Path(path).write_text(self.log_view.toPlainText(), encoding="utf-8")
        self._log("SYSTEM", f"Exported to {path}")

    def closeEvent(self, event):
        try:
            self.log_fp.close()
        except Exception:
            pass
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    win = BrowserLogger()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
