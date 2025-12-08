# SkyGuardian AI – Run Guide (Windows)

This project has three parts:
- `backend` (Flask + YOLOv8 API at `http://localhost:5000`)
- `frontend` (Vue 3 + Vite dev server at `http://localhost:8080`)
- `electron` (Desktop wrapper that loads the frontend)

Vite is already configured to proxy API calls to the backend at `/api`.

## Prerequisites
- Windows PowerShell 5.1 (default shell)
- Python 3.10 or 3.11 recommended
- Node.js 18+ (includes `npm`)
- Git (optional)

## 1) Set up and run the Backend (Flask)
The backend uses YOLOv8 (Ultralytics) and OpenCV.

1. Open PowerShell and go to the project root:
```powershell
cd "c:\Users\Mark\Documents\4th Year - 1st Sem\CSC 126\SoCiDetector"
```
2. (Recommended) Create and activate a virtual environment:
```powershell
python -m venv .venv
."\.venv\Scripts\Activate.ps1"
```
3. Install backend dependencies:
```powershell
pip install -r backend\requirements.txt
```
4. Ensure your YOLO model exists at `backend/model/best.pt`. If not, place your trained model there or update `MODEL_PATH` in `backend\app.py`.
5. Start the backend API server:
```powershell
python backend\app.py
```
The API should be available at `http://localhost:5000`. Health check: `http://localhost:5000/api/health`.

## 2) Set up and run the Frontend (Vite dev server)
In a new PowerShell window/tab:
```powershell
cd "c:\Users\Mark\Documents\4th Year - 1st Sem\CSC 126\SoCiDetector\frontend"
npm install
npm run dev
```
This starts Vite at `http://localhost:8080`. It proxies `/api` calls to `http://localhost:5000`.

## 3) Run the Electron app in development
Electron’s `main.js` loads `http://localhost:8080` when `NODE_ENV=development`.

In another PowerShell window/tab:
```powershell
cd "c:\Users\Mark\Documents\4th Year - 1st Sem\CSC 126\SoCiDetector\electron"
npm install
$env:NODE_ENV = "development"; npm start
```
This opens the desktop app. Ensure both backend and frontend are already running.

## 4) Build production files and package the desktop app (optional)
First build the frontend, then package Electron:
```powershell
cd "c:\Users\Mark\Documents\4th Year - 1st Sem\CSC 126\SoCiDetector\frontend"
npm run build

cd "c:\Users\Mark\Documents\4th Year - 1st Sem\CSC 126\SoCiDetector\electron"
npm run build
```
Electron Builder will look for `../frontend/dist` and create installers under `electron\dist`.

## Troubleshooting
- If backend prints `Model file not found`, verify `backend\model\best.pt` exists or update path.
- If Electron shows a blank page in dev, confirm `npm run dev` is running on port 8080.
- If API calls fail in dev, confirm backend is on port 5000; Vite proxy is set in `frontend\vite.config.js`.
- Torch/Ultralytics install issues: ensure Python version compatibility; for CPU-only, the pinned versions in `backend\requirements.txt` should work.

## Quick Start Summary
1) Backend: `python backend\app.py`
2) Frontend: `npm run dev` in `frontend`
3) Electron: `NODE_ENV=development; npm start` in `electron`

# Vue 3 + Vite

This template should help get you started developing with Vue 3 in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about IDE Support for Vue in the [Vue Docs Scaling up Guide](https://vuejs.org/guide/scaling-up/tooling.html#ide-support).
