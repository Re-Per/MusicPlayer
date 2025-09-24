"""Application entry point for the StreamFusion desktop prototype."""
from __future__ import annotations

import signal
import sys
import threading
import time
from typing import Tuple

import uvicorn
from PyQt5 import QtWidgets

from backend import create_app
from config import API_HOST, API_PORT
from frontend.gui import StreamFusionWindow


def _start_backend() -> Tuple[uvicorn.Server, threading.Thread]:
    """Launch the FastAPI backend in a background thread."""
    fastapi_app = create_app()
    config = uvicorn.Config(fastapi_app, host=API_HOST, port=API_PORT, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, name="StreamFusionBackend", daemon=True)
    thread.start()

    # Wait briefly for the server to start listening.
    timeout = time.time() + 5
    while not server.started and thread.is_alive() and time.time() < timeout:
        time.sleep(0.1)

    if not server.started:
        raise RuntimeError("Backend server failed to start in time.")

    return server, thread


def _stop_backend(server: uvicorn.Server, thread: threading.Thread) -> None:
    """Signal the backend thread to stop and wait for it to exit."""
    server.should_exit = True
    if thread.is_alive():
        thread.join(timeout=2)


def main() -> None:
    """Initialize backend + frontend and start the Qt event loop."""
    qt_app = QtWidgets.QApplication(sys.argv)

    try:
        server, thread = _start_backend()
    except Exception as exc:  # noqa: BLE001 - surface fatal startup issues
        QtWidgets.QMessageBox.critical(None, "Startup Error", f"Failed to start backend: {exc}")
        sys.exit(1)

    window = StreamFusionWindow()
    window.show()

    # Handle CTRL+C gracefully when running from console.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    exit_code = qt_app.exec_()
    _stop_backend(server, thread)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
