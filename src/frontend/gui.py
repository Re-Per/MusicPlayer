"""Frontend: PyQt5 window for interacting with StreamFusion backend."""
from __future__ import annotations

from pathlib import Path

from PyQt5 import QtCore, QtWidgets

from .api_client import upload_audio


class StreamFusionWindow(QtWidgets.QWidget):
    """Minimal desktop UI with an upload button and status messaging."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("StreamFusion Prototype")
        self.setMinimumSize(420, 220)
        self._status_label = QtWidgets.QLabel("Select a track to upload.")
        self._status_label.setAlignment(QtCore.Qt.AlignCenter)
        self._upload_button = QtWidgets.QPushButton("Upload My Music")
        self._upload_button.clicked.connect(self._handle_upload_clicked)

        layout = QtWidgets.QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self._status_label)
        layout.addSpacing(12)
        layout.addWidget(self._upload_button, alignment=QtCore.Qt.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

    def _handle_upload_clicked(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select an audio file",
            str(Path.home()),
            "Audio Files (*.mp3 *.wav *.flac *.aac *.ogg)",
        )
        if not file_path:
            return

        path = Path(file_path)
        try:
            payload = upload_audio(path)
        except Exception as exc:  # noqa: BLE001 - surface errors to users
            QtWidgets.QMessageBox.critical(
                self,
                "Upload Failed",
                f"Could not upload {path.name}.\n\nDetails: {exc}",
            )
            return

        self._status_label.setText(f"Upload Successful: {payload.get('original_name', path.name)}")
        QtWidgets.QMessageBox.information(
            self,
            "Upload Complete",
            f"Upload Successful: {payload.get('original_name', path.name)}",
        )
