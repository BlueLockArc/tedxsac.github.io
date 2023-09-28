@ECHO OFF
CD %1
setlocal enabledelayedexpansion

set "search=http://127.0.0.1:5000"
set "replace=https://tedxsac.up.railway.app"
set "files=assets/js/main.min.js"

echo Debug: Search string is "%search%"
echo Debug: Replace string is "%replace%"

for %%F in (%files%) do (
    echo Debug: Processing file %%F...

    for /f "tokens=*" %%A in ('powershell -command "(Get-Content '%%F') | ForEach-Object { $_ -replace [regex]::Escape('%search%'), '%replace%' } | Set-Content '%%F'"') do (
        echo Debug: Replacing in file %%F: %%A
    )

    echo Debug: Replacement complete for %%F!
)

git add -A > NULL
git commit -m "Website updates." > NULL
git push origin main > NUL
