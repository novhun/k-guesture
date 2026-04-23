@echo off
echo 🚀 Starting Windows Build Process...

:: 1. Clean previous builds
echo 🧹 Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: 2. Run PyInstaller
echo 📦 Bundling application with PyInstaller...
:: Note: Using ; as separator for Windows
venv\Scripts\pyinstaller --noconfirm --onefile --windowed ^
    --add-data "assets;assets" ^
    --add-data "hand_landmarker.task;." ^
    --name "K-Gesture" ^
    main.py

echo ✅ Success! Your EXE is ready at: dist\K-Gesture.exe
pause
