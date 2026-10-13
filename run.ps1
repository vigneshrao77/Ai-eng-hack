# ModernRx PowerShell CLI Helper

param(
    [Parameter(Position=0)]
    [string]$Command = "start"
)

$Host.UI.RawUI.WindowTitle = "ModernRx Application Advisor"

switch ($Command.ToLower()) {
    "start" {
        Write-Host ""
        Write-Host "========================================================" -ForegroundColor Cyan
        Write-Host "   ModernRx - Application Modernization Advisor" -ForegroundColor Green
        Write-Host "========================================================" -ForegroundColor Cyan
        Write-Host ""

        # Check Ollama status
        try {
            $ollamaCheck = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
            $models = ($ollamaCheck.models | ForEach-Object { $_.name }) -join ", "
            Write-Host "[AI] Local Ollama Detected: $models" -ForegroundColor Green
            Write-Host "[AI] Using Private Local Model for AI Twin & Architecture Council" -ForegroundColor DarkGreen
        } catch {
            Write-Host "[AI] Local Ollama not detected at :11434 (using fallback/Gemini)" -ForegroundColor Yellow
        }

        Write-Host ""
        Write-Host "Starting Backend on http://localhost:8000 ..." -ForegroundColor Cyan
        $backendProcess = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .venv\Scripts\uvicorn.exe app.main:app --app-dir backend --port 8000" -PassThru

        Write-Host "Starting Frontend on http://localhost:3000 ..." -ForegroundColor Cyan
        $frontendProcess = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev" -PassThru

        Write-Host ""
        Write-Host "Services launched successfully!" -ForegroundColor Green
        Write-Host "  -> Frontend UI : http://localhost:3000" -ForegroundColor White
        Write-Host "  -> Backend API : http://localhost:8000/docs" -ForegroundColor White
        Write-Host ""
        Write-Host "Opening web browser at http://localhost:3000 ..." -ForegroundColor Cyan
        Start-Sleep -Seconds 2
        Start-Process "http://localhost:3000"
    }

    "backend" {
        Write-Host "Starting ModernRx FastAPI Backend on http://localhost:8000..." -ForegroundColor Cyan
        & .venv\Scripts\uvicorn.exe app.main:app --app-dir backend --reload --port 8000
    }

    "frontend" {
        Write-Host "Starting Next.js Frontend on http://localhost:3000..." -ForegroundColor Cyan
        Set-Location frontend
        npm run dev
    }

    "test" {
        Write-Host "Running automated unit & integration tests..." -ForegroundColor Cyan
        & .venv\Scripts\pytest.exe tests/ -v
    }

    "lint" {
        Write-Host "Running code quality & security linters..." -ForegroundColor Cyan
        & .venv\Scripts\ruff.exe check backend/
    }

    "seed" {
        Write-Host "Seeding database with demo AcmeLIMS assessment and sample users..." -ForegroundColor Cyan
        & .venv\Scripts\python.exe scripts/seed_demo.py
    }

    default {
        Write-Host ""
        Write-Host "ModernRx Commands:" -ForegroundColor Cyan
        Write-Host "  .\run.ps1 start     - 1-Click Start: launches Backend (:8000), Frontend (:3000), and opens browser" -ForegroundColor Green
        Write-Host "  .\run.ps1 backend   - Start backend server on :8000" -ForegroundColor White
        Write-Host "  .\run.ps1 frontend  - Start Next.js frontend on :3000" -ForegroundColor White
        Write-Host "  .\run.ps1 test      - Run automated tests" -ForegroundColor White
        Write-Host "  .\run.ps1 lint      - Run ruff code linter" -ForegroundColor White
        Write-Host "  .\run.ps1 seed      - Reset & seed demo assessment" -ForegroundColor White
        Write-Host ""
    }
}
