"""Frontend: PyQt5 window for interacting with StreamFusion backend."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt5 import QtCore, QtMultimedia, QtWidgets

from ..config import UPLOADS_DIR
from .api_client import list_songs, upload_audio


class StreamFusionWindow(QtWidgets.QWidget):
    """Minimal desktop UI with upload, library, and playback controls."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("StreamFusion Prototype")
        self.setMinimumSize(520, 360)

        self._status_label = QtWidgets.QLabel("Select a track to upload or play.")
        self._status_label.setAlignment(QtCore.Qt.AlignCenter)

        self._upload_button = QtWidgets.QPushButton("Upload My Music")
        self._upload_button.clicked.connect(self._handle_upload_clicked)

        self._library_list = QtWidgets.QListWidget()
        self._library_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self._library_list.itemDoubleClicked.connect(self._handle_library_double_click)
        self._library_list.currentItemChanged.connect(lambda *_: self._update_controls_state())

        self._play_button = QtWidgets.QPushButton("Play Selected")
        self._play_button.clicked.connect(self._play_selected)
        self._stop_button = QtWidgets.QPushButton("Stop")
        self._stop_button.clicked.connect(self._stop_playback)

        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.addStretch()
        controls_layout.addWidget(self._play_button)
        controls_layout.addWidget(self._stop_button)
        controls_layout.addStretch()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._status_label)
        layout.addSpacing(8)
        layout.addWidget(self._upload_button, alignment=QtCore.Qt.AlignCenter)
        layout.addSpacing(12)
        library_label = QtWidgets.QLabel("My Library")
        library_label.setAlignment(QtCore.Qt.AlignLeft)
        library_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(library_label)
        layout.addWidget(self._library_list)
        layout.addLayout(controls_layout)
        self.setLayout(layout)

        self._player = QtMultimedia.QMediaPlayer(self)
        self._player.setVolume(70)
        self._player.stateChanged.connect(self._handle_player_state_change)

        self._update_controls_state()
        QtCore.QTimer.singleShot(250, self._refresh_library)

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

        original_name = payload.get("original_name", path.name)
        self._status_label.setText(f"Upload Successful: {original_name}")
        QtWidgets.QMessageBox.information(
            self,
            "Upload Complete",
            f"Upload Successful: {original_name}",
        )
        self._refresh_library(select_token=payload.get("stored_name"))

    def _refresh_library(self, select_token: Optional[str] = None) -> None:
        try:
            songs = list_songs()
        except Exception as exc:  # noqa: BLE001 - keep UI responsive on errors
            self._library_list.clear()
            self._status_label.setText(f"Could not load library: {exc}")
            self._update_controls_state()
            return

        self._library_list.clear()
        for song in songs:
            display_name = song.get("original_name") or song.get("stored_name") or "Unnamed"
            item = QtWidgets.QListWidgetItem(display_name)
            item.setData(QtCore.Qt.UserRole, song.get("stored_name"))
            item.setData(QtCore.Qt.UserRole + 1, display_name)
            self._library_list.addItem(item)

        if select_token:
            for index in range(self._library_list.count()):
                item = self._library_list.item(index)
                if item.data(QtCore.Qt.UserRole) == select_token:
                    self._library_list.setCurrentItem(item)
                    break
        elif self._library_list.count() > 0:
            self._library_list.setCurrentRow(0)

        if self._library_list.count() == 0:
            self._status_label.setText("Library empty. Upload your first track!")
        else:
            total = self._library_list.count()
            noun = "track" if total == 1 else "tracks"
            self._status_label.setText(f"Library refreshed: {total} {noun} available.")

        self._update_controls_state()

    def _play_selected(self) -> None:
        item = self._library_list.currentItem()
        if item is None:
            QtWidgets.QMessageBox.information(self, "No Selection", "Please choose a track to play.")
            return

        stored_name = item.data(QtCore.Qt.UserRole)
        if not stored_name:
            QtWidgets.QMessageBox.warning(self, "Missing File", "Selected entry does not have an associated file.")
            return

        file_path = UPLOADS_DIR / stored_name
        if not file_path.exists():
            QtWidgets.QMessageBox.warning(
                self,
                "File Missing",
                "The requested file could not be found on disk. It may have been moved or deleted.",
            )
            self._refresh_library()
            return

        media = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(str(file_path)))
        self._player.setMedia(media)
        self._player.play()

        original_name = item.data(QtCore.Qt.UserRole + 1) or file_path.name
        self._status_label.setText(f"Playing: {original_name}")

    def _stop_playback(self) -> None:
        if self._player.state() != QtMultimedia.QMediaPlayer.StoppedState:
            self._player.stop()
            self._status_label.setText("Playback stopped.")

    def _handle_library_double_click(self, item: QtWidgets.QListWidgetItem) -> None:
        if item:
            self._library_list.setCurrentItem(item)
            self._play_selected()

    def _handle_player_state_change(self, state: QtMultimedia.QMediaPlayer.State) -> None:
        if state == QtMultimedia.QMediaPlayer.StoppedState:
            # Keep friendly messaging when track naturally ends.
            if self._player.mediaStatus() == QtMultimedia.QMediaPlayer.EndOfMedia:
                self._status_label.setText("Playback finished.")

    def _update_controls_state(self) -> None:
        has_selection = self._library_list.currentItem() is not None
        self._play_button.setEnabled(has_selection)
        self._stop_button.setEnabled(self._player.state() != QtMultimedia.QMediaPlayer.StoppedState)
