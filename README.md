# SkyGuardian AI (SoCiDetector)

End-to-end desktop app for aerial threat detection using YOLO, with a Flask backend, Vue/Vite frontend, and Electron wrapper.

## Prerequisites
- Windows 10/11
- Git
- Node.js 18+ (includes npm)
- Python 3.11

## First-Time Setup
1) Clone and enter the repo
```
git clone <your-fork-or-repo-url>
cd SoCiDetector
```

2) Python environment (backend)
```
python -m venv .venv311
.\.venv311\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r backend\requirements.txt
```

3) Frontend dependencies
```
cd frontend
npm install
cd ..
```

4) Electron dependencies
```
cd electron
npm install
cd ..
```

## Model File
- Place your trained model at `backend\model\best.pt` (recommended) or set an absolute path with the `MODEL_PATH` env variable.
- Note: model files (`*.pt`) are large and are ignored by Git by default.

## Run (Development)
Open three terminals and run each section.

1) Backend (Flask)
```
cd "c:\Users\Mark\Documents\4th Year - 1st Sem\CSC 126\SoCiDetector"
$py311 = Join-Path $PWD ".venv311\Scripts\python.exe"
$env:MODEL_PATH = "c:\Users\Mark\Documents\4th Year - 1st Sem\CSC 126\SoCiDetector\backend\model\best.pt"
& $py311 backend\app.py
```
Health check: `http://localhost:5000/api/health` should show `model_loaded: true`.

2) Frontend (Vite dev server)
```
cd frontend
npm run dev
```
Default URL: `http://localhost:8080` (proxy to backend at `http://localhost:5000`).

3) Electron (loads the dev server)
```
cd electron
$env:NODE_ENV = "development"
$env:FRONTEND_PORT = "8080"   # match Vite dev port
npm start
```

## Run (Production-ish locally)
Build the frontend and launch Electron against the built files.
```
cd frontend
npm run build

cd ..\electron
$env:NODE_ENV = "production"
npm start
```

## Packaging (Windows installer)
```
cd electron
npm run build
```
The installer/AppImage will be output in `electron\dist`.

## Troubleshooting
- Model not loaded:
  - Verify the path in `/api/health` (`model_path`).
  - Use `POST /api/reload-model` with `{ "model_path": "C:\\path\\to\\best.pt" }`.
  - Ensure Git is installed (YOLOv5 hub/local fallback uses it).
- Port conflicts:
  - If Vite uses a different port, set `FRONTEND_PORT` to that exact port before `npm start` in Electron.
- Python version:
  - Use Python 3.11. Some packages fail to build on 3.12.

## Git Hygiene
This repo ignores:
- Python venvs (`.venv*`), caches, and build artifacts
- Node `node_modules`, `dist` outputs
- Uploads and large model files (`*.pt`)

If you need to share a trained model, publish it separately (e.g., release asset) and reference it via `MODEL_PATH`.
