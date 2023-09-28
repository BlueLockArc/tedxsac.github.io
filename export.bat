@ECHO OFF
CD %1
setlocal enabledelayedexpansion

set "search=http://127.0.0.1:5000"
set "replace=https://tedxsac.up.railway.app"
set "files=index.html admin.html registration.html"

for %%F in (%files%) do (
    for /f "tokens=*" %%A in ('powershell -command "(Get-Content '%%F') | ForEach-Object { $_ -replace [regex]::Escape('%search%'), '%replace%' } | Set-Content '%%F'"') do (
        echo %%A
    )

    echo Replacement complete for %%F!
)

git add -A
git commit -m "Website updates." 
git push origin main > NUL
