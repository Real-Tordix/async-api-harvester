from __future__ import annotations

import asyncio
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from async_api_harvester.config import HarvesterConfig
from async_api_harvester.harvester import APIHarvester


class ApiHarvestWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Async API Harvester")
        self.resize(980, 620)
        self._build_ui()

    def _build_ui(self) -> None:
        container = QWidget(self)
        self.setCentralWidget(container)

        root = QVBoxLayout(container)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        title = QLabel("API Harvest Dashboard")
        title.setObjectName("title")
        root.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://jsonplaceholder.typicode.com/posts/1")
        form.addRow("URL", self.url_input)

        self.mode_box = QComboBox()
        self.mode_box.addItems(["Single URL", "Demo URLs", "Custom list"])
        form.addRow("Mode", self.mode_box)

        self.concurrency_input = QLineEdit("5")
        self.timeout_input = QLineEdit("5.0")
        self.retries_input = QLineEdit("3")

        form.addRow("Concurrency", self.concurrency_input)
        form.addRow("Timeout", self.timeout_input)
        form.addRow("Retries", self.retries_input)

        root.addLayout(form)

        actions = QHBoxLayout()
        self.run_button = QPushButton("Run harvest")
        self.clear_button = QPushButton("Clear log")
        actions.addWidget(self.run_button)
        actions.addWidget(self.clear_button)
        root.addLayout(actions)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Harvest output will appear here...")
        root.addWidget(self.log_output, 1)

        self.run_button.clicked.connect(self.run_harvest)
        self.clear_button.clicked.connect(self.log_output.clear)

    def run_harvest(self) -> None:
        try:
            target_urls = self._resolve_urls()
            concurrency = int(self.concurrency_input.text())
            timeout = float(self.timeout_input.text())
            retries = int(self.retries_input.text())
        except ValueError as exc:
            QMessageBox.warning(self, "Input error", f"Invalid numeric input: {exc}")
            return

        if not target_urls:
            QMessageBox.warning(self, "No URLs", "Please add at least one valid URL.")
            return

        config = HarvesterConfig(
            concurrency=concurrency,
            timeout=timeout,
            retries=retries,
        )
        harvester = APIHarvester(config=config)

        self.log_output.append("Starting harvest...")
        try:
            results = asyncio.run(harvester.collect(target_urls))
        except Exception as exc:  # pragma: no cover - GUI safety path
            self.log_output.append(f"Harvest failed: {exc}")
            return

        if not results:
            self.log_output.append("No results returned.")
            return

        for result in results:
            self.log_output.append(result.summary())

        self.log_output.append(f"Completed: {len(results)} successful fetch(es)")

    def _resolve_urls(self) -> list[str]:
        mode = self.mode_box.currentText()
        if mode == "Single URL":
            url = self.url_input.text().strip()
            return [url] if url else []
        if mode == "Demo URLs":
            return [
                "https://jsonplaceholder.typicode.com/posts/1",
                "https://jsonplaceholder.typicode.com/posts/2",
                "https://jsonplaceholder.typicode.com/posts/3",
            ]
        url = self.url_input.text().strip()
        return [part.strip() for part in url.split(",") if part.strip()]


def launch_gui() -> None:
    import sys

    app = QApplication(sys.argv)
    css_path = Path(__file__).with_name("styles.css")
    stylesheet = css_path.read_text(encoding="utf-8")
    app.setStyleSheet(stylesheet)

    window = ApiHarvestWindow()
    window.show()
    sys.exit(app.exec_())
