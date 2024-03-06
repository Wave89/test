rem rmdir /s /q venv
C:\Python39\python.exe -m venv .\venv
%cd%\venv\Scripts\python.exe -m pip install --upgrade pip
%cd%\venv\Scripts\pip install -r requirements.txt --upgrade
%cd%\venv\Scripts\python.exe -m pip freeze > %cd%\requirements_backup.txt
del %cd%\requirements_backup_version.txt
@echo off
echo python version: >> %cd%\requirements_backup_version.txt
%cd%\venv\Scripts\python.exe --version >> %cd%\requirements_backup_version.txt
echo pip version: >> %cd%\requirements_backup_version.txt
%cd%\venv\Scripts\python.exe -m pip --version >> %cd%\requirements_backup_version.txt
pause