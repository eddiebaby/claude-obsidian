@echo off
rem Scheduled by Windows Task Scheduler ("RSA alert scan"): scan, push new buys via ntfy, log the run.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
if not exist data\rsa mkdir data\rsa
rem After a wake from sleep, Wi-Fi can lag the task by a minute: wait up to 5 minutes for DNS.
for /l %%i in (1,1,10) do (
  "C:\Users\scott\AppData\Local\Programs\Python\Python313\python.exe" -c "import socket; socket.gethostbyname('efts.sec.gov')" >nul 2>&1 && goto scan
  rem ping, not timeout: timeout quits at once when the task has no console input
  ping -n 31 127.0.0.1 >nul
)
echo ===== %date% %time% no network after 5 minutes, scanning anyway >> data\rsa\alert.log
:scan
echo ===== %date% %time% >> data\rsa\alert.log
"C:\Users\scott\AppData\Local\Programs\Python\Python313\python.exe" run_rsa.py --alert >> data\rsa\alert.log 2>&1
