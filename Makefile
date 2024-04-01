# Makefile for PyInstaller macOS .app compilation
APP_NAME = AutoMatrix

# Build the .app bundle
build:
	pyinstaller main.spec

# Clean up build artifacts
clean:
	rm -rf build dist

# Run the compiled .app from the terminal
run:
	./dist/$(APP_NAME)

# Create a macOS Disk Image (DMG) for distribution
create_dmg:
	hdiutil create -volname $(APP_NAME) -srcfolder dist -ov -format UDZO $(APP_NAME).dmg
