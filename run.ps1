# Script to run both frontend and backend servers

Write-Host "🚀 Starting AI Population Analysis System..." -ForegroundColor Green
Write-Host ""

# Start backend server
Write-Host "📊 Starting Backend Server (Port 8000)..." -ForegroundColor Cyan
$backendProcess = Start-Process -FilePath "python" `
    -ArgumentList "-m uvicorn app.main:app --reload --port 8000" `
    -WorkingDirectory "d:\AI python\backend" `
    -NoNewWindow `
    -PassThru

Write-Host "✅ Backend started (PID: $($backendProcess.Id))" -ForegroundColor Green

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend development server
Write-Host "🎨 Starting Frontend Server (Port 5173)..." -ForegroundColor Cyan
$frontendProcess = Start-Process -FilePath "npm" `
    -ArgumentList "run dev" `
    -WorkingDirectory "d:\AI python\frontend" `
    -NoNewWindow `
    -PassThru

Write-Host "✅ Frontend started (PID: $($frontendProcess.Id))" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access the application:" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host "   Backend:  http://localhost:8000/api" -ForegroundColor Yellow
Write-Host ""
Write-Host "⏹️  Press Ctrl+C to stop all servers" -ForegroundColor Yellow
Write-Host ""

# Keep script running
$null = $backendProcess.WaitForExit()
