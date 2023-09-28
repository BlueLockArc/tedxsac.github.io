@ECHO OFF
CD %1
setlocal enabledelayedexpansion

set "search=http://127.0.0.1:5000"
set "replace=https://tedxsac.up.railway.app"
set "files=assets/js/main.min.js assets/js/Display-table.min.js"

REM Loop through each file
for %%F in (%files%) do (
    REM Use PowerShell to perform search and replace
    for /f "tokens=*" %%A in ('powershell -command "(Get-Content '%%F') | ForEach-Object { $_ -replace [regex]::Escape('%search%'), '%replace%' } | Set-Content '%%F'"') do (
        REM No debug output in this version
    )
)

REM Stage, commit, and push changes using Git
git add -A > NUL
git commit -m "Website updates." > NUL
git push origin main > NUL
