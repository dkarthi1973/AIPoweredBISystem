@echo off
REM Check if port number is provided
IF "%1"=="" (
    echo Usage: killport.bat [port_number]
    exit /b 1
)

REM Find the PID using the specified port
FOR /F "tokens=5" %%a IN ('netstat -ano ^| findstr :%1') DO (
    SET PID=%%a
)

REM Check if PID was found
IF NOT DEFINED PID (
    echo No process found using port %1.
    exit /b 1
)

REM Kill the process
echo Killing process with PID %PID% using port %1...
taskkill /PID %PID% /F
