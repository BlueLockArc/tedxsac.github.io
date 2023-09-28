@ECHO  OFF
CD %1 
setlocal enabledelayedexpansion

set "search=http://127.0.0.1:5000"
set "replace=https://tedxsac.up.railway.app"
set "files=index.html admin.html registration.html"

for %%F in (%files%) do (
    set "input_file=%%F"
    set "output_file=%%~nF_modified.html"

    for /f "tokens=*" %%A in ('powershell -command "(Get-Content '!input_file!') | ForEach-Object { $_ -replace [regex]::Escape('%search%'), '%replace%' } | Set-Content '!output_file!'"') do (
        echo %%A
    )

    echo Replacement complete for !input_file!. Modified output saved to !output_file!
)
git add -A
git commit -m "Website updates." 
git push origin main
