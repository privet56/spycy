set "PATH=%~dp0..\devenv\git;%~dp0..\devenv\git\bin;%~dp0..\devenv\git\usr\bin;%PATH%"
set "PATH=%~dp0..\devenv\nodejs;%~dp0..\devenv\nodejs\node_modules\npm;%PATH%"
set "PATH=%~dp0..\devenv\conda;%~dp0..\devenv\conda\Scripts;%~dp0..\devenv\conda\Library\bin;%PATH%"

set PYTHON=%~dp0..\devenv\conda\python.exe

set APPDATA=%~dp0../devenv/MsVSCode
set USERPROFILE=%~dp0../devenv/MsVSCode

start "" %~dp0../devenv/MsVSCode/Code.exe %~dp0
