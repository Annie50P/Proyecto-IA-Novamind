Write-Host "====================================="
Write-Host " INICIANDO PROYECTO NOVAMIND IA "
Write-Host "====================================="

# 1. Verificar entorno virtual
if (-Not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: No se encontro el entorno virtual (.venv)"
    Write-Host "Crea el entorno con: python -m venv .venv"
    exit
}

# 2. Activar entorno virtual
Write-Host "Activando entorno virtual..."
& .\.venv\Scripts\Activate.ps1

# 3. Instalar dependencias necesarias
Write-Host "Verificando dependencias..."
pip install --quiet -r backend/requirements.txt
pip install --quiet -r frontend/requirements.txt
pip install --quiet python-multipart

# 4. Iniciar BACKEND
Write-Host "Iniciando BACKEND (FastAPI)..."
Start-Process powershell -ArgumentList "
cd '$PWD';
.\.venv\Scripts\Activate.ps1;
uvicorn backend.main:app --reload --port 8000
"

# Esperar a que backend levante
Start-Sleep -Seconds 3

# 5. Iniciar FRONTEND PUBLICO
Write-Host "Iniciando FRONTEND PUBLICO..."
Start-Process powershell -ArgumentList "
cd '$PWD';
.\.venv\Scripts\Activate.ps1;
streamlit run frontend/app_publica.py
"

# 6. Iniciar FRONTEND RRHH
Write-Host "Iniciando FRONTEND RRHH..."
Start-Process powershell -ArgumentList "
cd '$PWD';
.\.venv\Scripts\Activate.ps1;
streamlit run frontend/app_rrhh.py
"

Write-Host ""
Write-Host "PROYECTO LEVANTADO CORRECTAMENTE"
Write-Host "Backend:  http://127.0.0.1:8000/docs"
Write-Host "Publico:  http://localhost:8501"
Write-Host "RRHH:     http://localhost:8502"
Write-Host ""
