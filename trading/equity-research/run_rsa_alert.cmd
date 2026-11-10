@echo off
rem Scheduled by Windows Task Scheduler ("RSA alert scan"): scan, push new buys via ntfy, log the run.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if not exist data\rsa mkdir data\rsa
echo ===== %date% %time% >> data\rsa\alert.log
"C:\Users\scott\AppData\Local\Programs\Python\Python313\python.exe" run_rsa.py --alert >> data\rsa\alert.log 2>&1
