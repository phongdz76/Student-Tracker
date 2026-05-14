@echo off
echo ========================================================
echo DONG GOI PHAN MEM STUDENT TRACKER (PYINSTALLER)
echo ========================================================
echo.
echo 1. Dang cai dat PyInstaller...
pip install pyinstaller

echo.
echo 2. Dang tien hanh dong goi gui.py thanh file .exe...
echo Qua trinh nay co the mat 1-2 phut, vui long cho doi...
python -m PyInstaller --noconfirm --onedir --windowed --name "Student Tracker" "gui.py"

echo.
echo ========================================================
echo HOAN THANH! 
echo Phan mem cua ban da nam trong thu muc 'dist\Student Tracker'
echo Ban co the gui toan bo thu muc do cho ban be de chay truc tiep!
echo ========================================================
pause
