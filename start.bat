@echo off
cd /d "c:\Users\user\Desktop\REPOSITORIOS GIT\microservicio-stock"
echo Iniciando servidor FastAPI con entorno virtual...
.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause