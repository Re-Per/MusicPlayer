# StreamFusion Prototype

StreamFusion is a desktop proof-of-concept that blends the polish of major streaming platforms with room for future expansion. This prototype delivers a Python FastAPI backend, a PyQt5 desktop frontend, and a simple SQLite metadata store packaged into a single executable.

## Features
- Desktop app window titled "StreamFusion Prototype" with an **Upload My Music** button
- Audio file upload support (MP3, WAV, AAC, FLAC, OGG)
- Files stored locally under `/uploads` and metadata captured in `/db/streamfusion.db`
- REST endpoints (`/upload`, `/list-songs`) ready for future integrations

## Project Layout
```
.
|-- src/
|   |-- app.py                # Entry point launching backend + frontend
|   |-- config.py             # Shared path + runtime configuration
|   |-- backend/              # FastAPI server, storage, and SQLite helpers
|   `-- frontend/             # PyQt5 UI and HTTP client
|-- uploads/                  # User-uploaded audio files
|-- db/                       # SQLite database location
|-- dist/                     # Generated executables (after build)
|-- requirements.txt          # Python dependencies
`-- README.md                 # Project documentation
```

## Prerequisites
- Python 3.10+
- `pip` available on PATH

## Setup & Usage
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run locally for development**
   ```bash
   python src/app.py
   ```
   The GUI opens and the backend listens on `http://127.0.0.1:8765`.
3. **Build the Windows executable**
   ```bash
   pyinstaller --onefile --noconsole src/app.py -n StreamFusion
   ```
   The resulting `StreamFusion.exe` will be generated under `dist/`.
4. **Launch the packaged app**
   Double-click `dist/StreamFusion.exe`.

> The application ensures required folders (`uploads`, `db`) exist beside the executable at runtime.

## Roadmap Hooks
- Authentication, user profiles, and subscription logic can attach to FastAPI routes.
- Streaming playback interfaces plug into the backend once transcoding/storage services are defined.
- A "Discover" feed can extend the `/list-songs` endpoint and PyQt frontend widgets.
- Artist dashboards and analytics can reuse the SQLite layer or upgrade to a larger database later.
