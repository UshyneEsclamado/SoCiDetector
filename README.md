# SkyGuardian AI (SoCiDetector)

SkyGuardian AI is a Windows desktop application for aerial threat detection and classification. It combines a YOLO-based inference backend, a real-time Vue dashboard, and an Electron shell so analysts can run detections entirely offline.

## Table of Contents
1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Repository Layout](#repository-layout)
4. [Prerequisites](#prerequisites)
5. [Setup Guide](#setup-guide)
6. [Running the System](#running-the-system)
7. [Model Management](#model-management)
8. [Key Features & UX Notes](#key-features--ux-notes)
9. [API & Health Checks](#api--health-checks)
10. [Packaging & Distribution](#packaging--distribution)
11. [Troubleshooting](#troubleshooting)
12. [Git Hygiene](#git-hygiene)

## System Overview
- **Use case:** detect and classify soldiers vs civilians from aerial footage/images.
- **Workflow:** user uploads an image/video → backend runs YOLOv8 by default (auto-falls back to YOLOv5 weights) → annotated frames stream back to the frontend → detections are grouped into “sessions” for review.
- **Offline-first:** all processing happens locally; no internet connection required once dependencies and the trained model are present.

## Technology Stack
| Layer | Tech | Notes |
| --- | --- | --- |
| Backend | Python 3.11, Flask 3, Torch 2.1, Ultralytics YOLOv8 + YOLOv5 fallback, OpenCV | Serves `/api/*` endpoints, handles inference, keeps detection history |
| Frontend | Vue 3 (Composition API), Vite 7, Axios | Real-time dashboard, session grouping, statistics, uploads |
| Desktop | Electron 28 | Wraps the Vite app for a native Windows experience |
| Tooling | Node.js 18+, npm, git | Required for dev/build |

## Repository Layout
```
SoCiDetector/
├─ backend/        # Flask app, YOLO loaders, requirements.txt
├─ frontend/       # Vue 3 + Vite source
│  ├─ src/components/ (VideoPlayer, DetectionPanel, ResultHistory, etc.)
│  └─ services/api.js
└─ electron/       # Electron main process + builder config
```

## Prerequisites
- Windows 10/11 (x64)
- Python 3.11 (installed per-user, add to PATH)
- Node.js 18+ (comes with npm)
- Git (required for YOLOv5 hub fallback)

## Setup Guide
1. **Clone the repository**
   ```powershell
   git clone https://github.com/UshyneEsclamado/SoCiDetector.git
   cd SoCiDetector
   ```

2. **Create the Python virtual environment**
   ```powershell
   python -m venv .venv311
   .\.venv311\Scripts\activate
   python -m pip install --upgrade pip setuptools wheel
   pip install -r backend\requirements.txt
   ```

3. **Install frontend dependencies**
   ```powershell
   cd frontend
   npm install
   cd ..
   ```

4. **Install Electron dependencies**
   ```powershell
   cd electron
   npm install
   cd ..
   ```

## Running the System
Use three terminals (backend, frontend, electron). Replace paths if you cloned elsewhere.

### 1) Backend (Flask + YOLO)
```powershell
cd "c:\Users\Mark\Documents\4th Year - 1st Sem\CSC 126\SoCiDetector"
$py311 = Join-Path $PWD ".venv311\Scripts\python.exe"
$env:MODEL_PATH = "c:\Users\Mark\Documents\4th Year - 1st Sem\CSC 126\SoCiDetector\backend\model\best.pt"
& $py311 backend\app.py
```
Verify health: `Invoke-RestMethod http://localhost:5000/api/health` (should return `model_loaded:true`).

### 2) Frontend (Vite dev server)
```powershell
cd frontend
npm run dev
```
Default dev URL: `http://localhost:8080` (proxy to backend at port 5000). If Vite auto-picks another port (e.g., 8081), note it for Electron.

### 3) Electron shell (loads dev server)
```powershell
cd electron
$env:NODE_ENV = "development"
$env:FRONTEND_PORT = "8080"   # match the Vite port
npm start
```

### Production-style run (optional)
```powershell
cd frontend
npm run build

cd ..\electron
$env:NODE_ENV = "production"
npm start
```
Electron loads the built assets from `frontend/dist` instead of the live dev server.

## Model Management
- **Default path:** `backend\model\best.pt`. The backend reads `MODEL_PATH`; set it before launching so different weight files can be tested quickly.
- **YOLOv5 fallback:** If the supplied `.pt` file is YOLOv5-based, the backend automatically switches loaders (Torch Hub → local repo) and patches Windows-specific path issues.
- **Obtaining `best.pt`:** export from your Colab training notebook via Ultralytics `model.export(format="torchscript")` or copy `runs/train/.../weights/best.pt` from Google Drive. Place it in `backend/model/` or anywhere accessible and point `MODEL_PATH` to it.
- **Large files:** `.pt` weights are ignored by git; distribute via cloud storage or removable media.

## Key Features & UX Notes
- **Session-aware history:** each upload (image or video) is grouped, with the original frame, annotated frame, timestamp, and detection count. Re-selecting a session refreshes the Detection Panel and Statistics cards.
- **Video throttling:** frames are sampled at a steady rate (~3 FPS) and processing stops automatically when the clip finishes, preventing duplicate detections from the last frame.
- **Statistics widget:** totals, soldier/civilian counts, and percentages update live as detections stream in.
- **Manual capture:** use “📸 Capture Frame” to export the current canvas.

## API & Health Checks
| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/health` | GET | Returns `{ status, model_loaded, model_backend, model_path, error }` |
| `/api/reload-model` | POST | Body `{ model_path?: str }`; reloads weights without restarting Flask |
| `/api/detect/image` | POST | Accepts base64 JPEG frame; returns detections + annotated image |
| `/api/detect/video-frame` | POST | Alias of `/api/detect/image` for streaming |
| `/api/upload-video` | POST (multipart) | Saves uploaded video and returns metadata (fps, duration, etc.) |
| `/api/statistics` | GET | Overall counts + last 10 detections |
| `/api/clear-history` | POST | Wipes detection history |

Use `Invoke-RestMethod` or your favorite REST client for debugging.

## Packaging & Distribution
Generate an installer/build artifacts via electron-builder:
```powershell
cd electron
npm run build
```
Outputs go to `electron/dist` (NSIS installer on Windows). Ensure you run `npm run build` in `frontend/` beforehand so Electron bundles the latest UI.

## Troubleshooting
- **Model not loaded**
  - Confirm `MODEL_PATH` points to an existing `.pt` file.
  - Hit `/api/health` to read the `error` field for YOLOv8/v5 loader details.
  - Git must be installed for Torch Hub to fetch YOLOv5 dependencies.
- **Ports already in use**
  - Close previous dev servers or change the Vite port (`npm run dev -- --port 8081`). Remember to update `FRONTEND_PORT` for Electron.
- **Python errors on 3.12**
  - Use Python 3.11. Torch/Ultralytics wheels are not ready for 3.12 yet.
- **Video detection loops**
  - The player now stops once playback reaches the end. If detections still accumulate, ensure the backend processed the final frame (watch the backend console for completion logs).

## Git Hygiene
Items ignored by `.gitignore`:
- `.venv*/`, `__pycache__/`, `*.pyc`, build artifacts
- `frontend/node_modules/`, `frontend/dist/`, Vite cache
- `electron/node_modules/`, `electron/dist/`
- `backend/uploads/`, `backend/model/*.pt|*.onnx|*.pth`


