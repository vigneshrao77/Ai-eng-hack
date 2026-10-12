# ModernRx PowerShell CLI Helper

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

switch ($Command) {
    "test" {
        & .venv\Scripts\pytest.exe tests/ -v
    }
    "lint" {
        & .venv\Scripts\ruff.exe check backend/
    }
    "seed" {
        & .venv\Scripts\python.exe scripts/seed_demo.py
    }
    "backend" {
        & .venv\Scripts\uvicorn.exe app.main:app --app-dir backend --reload --port 8000
    }
    "frontend" {
        Set-Location frontend
        npm run dev
    }
    default {
        Write-Host "ModernRx CLI Commands:"
        Write-Host "  .\run.ps1 test      - Run automated tests"
        Write-Host "  .\run.ps1 lint      - Run ruff linter"
        Write-Host "  .\run.ps1 seed      - Seed demo AcmeLIMS assessment and users"
        Write-Host "  .\run.ps1 backend   - Start backend server on :8000"
        Write-Host "  .\run.ps1 frontend  - Start Next.js frontend on :3000"
    }
}
