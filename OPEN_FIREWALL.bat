@echo off
echo Opening Windows Firewall for port 8000...
netsh advfirewall firewall add rule name="FastAPI Backend" dir=in action=allow protocol=TCP localport=8000
echo.
echo Firewall rule added successfully!
echo.
pause
