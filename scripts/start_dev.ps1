# Start Backend and Frontend concurrently for Windows development
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " NetProtocol Inspector - Development Environment Starter   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$CurrentDir = Get-Location

# 1. Initialize DB and Demo PCAP
Write-Host "[1/3] Initializing Database & Demo Capture..." -ForegroundColor Yellow
python scripts/init_db.py
python scripts/generate_sample_pcap.py

# 2. Start Backend in separate window
Write-Host "[2/3] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

# 3. Start Frontend in current window
Write-Host "[3/3] Starting React Frontend on http://localhost:5173..." -ForegroundColor Green
cd frontend
npm run dev
