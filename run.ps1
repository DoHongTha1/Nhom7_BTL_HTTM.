# Script to run both frontend and backend servers

Write-Host "Starting AI Population Analysis System..." -ForegroundColor Green
Write-Host ""

# Start backend server
Write-Host "Starting Backend Server (Port 8000)..." -ForegroundColor Cyan
$backendProcess = Start-Process -FilePath "python" `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000" `
    -WorkingDirectory "d:\AI python\backend" `
    -NoNewWindow `
    -PassThru

Write-Host "Backend started (PID: $($backendProcess.Id))" -ForegroundColor Green

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend development server
Write-Host "Starting Frontend Server (Port 5173)..." -ForegroundColor Cyan
$frontendProcess = Start-Process -FilePath "C:\Program Files\nodejs\npm.cmd" `
    -ArgumentList "run", "dev" `
    -WorkingDirectory "d:\AI python\frontend" `
    -NoNewWindow `
    -PassThru

Write-Host "Frontend started (PID: $($frontendProcess.Id))" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host "Backend:  http://localhost:8000/api" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Yellow
Write-Host ""

# Keep script running until user stops it
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "Stopping servers..." -ForegroundColor Yellow
    Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    Write-Host "All servers stopped." -ForegroundColor Green
}
