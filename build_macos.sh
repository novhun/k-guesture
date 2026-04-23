#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting macOS Build Process..."

# 1. Clean previous builds
echo "🧹 Cleaning old build files..."
rm -rf build dist

# 2. Run PyInstaller
echo "📦 Bundling application with PyInstaller..."
venv/bin/pyinstaller --noconfirm --windowed \
    --add-data "assets:assets" \
    --add-data "hand_landmarker.task:." \
    --name "K-Gesture" \
    main.py

# 3. Create DMG
echo "💿 Creating DMG installer..."
mkdir -p dist/dmg
cp -r dist/K-Gesture.app dist/dmg/

# Check if hdiutil exists (standard on macOS)
if command -v hdiutil &> /dev/null; then
    hdiutil create -volname "K-Gesture" -srcfolder dist/dmg -ov -format UDZO dist/K-Gesture.dmg
    echo "✅ Success! Your DMG is ready at: dist/K-Gesture.dmg"
else
    echo "⚠️ hdiutil not found. You can manually zip the .app folder in dist/ instead."
fi

# 4. Cleanup
rm -rf dist/dmg
echo "✨ Build Complete!"
