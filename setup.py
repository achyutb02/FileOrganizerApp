# setup.py - Use this to create a standalone executable
# Run: pip install pyinstaller
# Then: python setup.py

import os
import subprocess
import sys
import shutil

def create_executable():
    """Create a standalone executable using PyInstaller"""
    
    print("=" * 60)
    print("File Organizer v2 - Executable Builder")
    print("=" * 60)
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found!")
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed!")
        print()
    
    print("🔨 Building executable...")
    print("This may take a few minutes...")
    print()
    
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    try:
        # Build the executable
        if sys.platform == 'darwin':  # macOS
            print("Building for macOS...")
            subprocess.check_call([
                'pyinstaller',
                '--clean',
                '--windowed',
                '--name=FileOrganizer',
                '--onefile',
                'file_organizer_v2.py'
            ])
            
            # Move the app to a better location
            output_dir = "FileOrganizer_Ready_To_Use"
            os.makedirs(output_dir, exist_ok=True)
            
            # Copy the .app bundle
            if os.path.exists('dist/FileOrganizer.app'):
                dest = os.path.join(output_dir, 'FileOrganizer.app')
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree('dist/FileOrganizer.app', dest)
            
            # Create a README
            readme = """
╔════════════════════════════════════════════════════════════╗
║           FILE ORGANIZER V2 - READY TO USE!               ║
╚════════════════════════════════════════════════════════════╝

📦 YOUR APP IS HERE: FileOrganizer.app

🚀 HOW TO INSTALL:
   1. Drag "FileOrganizer.app" to your Applications folder
   2. Double-click to open!

⚠️  FIRST TIME OPENING:
   macOS may show a security warning because this app
   is not from the App Store.
   
   If blocked:
   • Go to System Preferences → Security & Privacy
   • Click "Open Anyway" at the bottom
   • Or right-click the app → Open → confirm

✅ AFTER THAT:
   The app will open normally every time!

📁 WHAT IT DOES:
   • Organize messy folders automatically
   • Sort by file type, date, size, or smart categories
   • Preview before organizing
   • Undo if you don't like the result

💡 TIP: You can delete all other files/folders in this
   directory - you only need FileOrganizer.app

Enjoy organizing your files! 🎉
"""
            
            with open(os.path.join(output_dir, 'README.txt'), 'w') as f:
                f.write(readme)
            
            print()
            print("=" * 60)
            print("✅ SUCCESS! Your app is ready!")
            print("=" * 60)
            print()
            print(f"📁 Look in the folder: {output_dir}/")
            print()
            print("👉 EVERYTHING YOU NEED IS IN THAT FOLDER!")
            print()
            print("   • FileOrganizer.app ← This is your app!")
            print("   • README.txt ← Instructions for users")
            print()
            print("🎁 Share the entire folder with anyone!")
            print("   They don't need Python or any coding tools.")
            
        elif sys.platform == 'win32':  # Windows
            print("Building for Windows...")
            print("Using --onedir mode for better compatibility...")
            
            # Use --onedir instead of --onefile for better Windows compatibility
            subprocess.check_call([
                'pyinstaller',
                '--clean',
                '--windowed',
                '--name=FileOrganizer',
                '--onedir',  # Changed from --onefile
                '--noconfirm',
                'file_organizer_v2.py'
            ])
            
            # Move to a better location
            output_dir = "FileOrganizer_Ready_To_Use"
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            os.makedirs(output_dir, exist_ok=True)
            
            # Copy the entire folder
            if os.path.exists('dist/FileOrganizer'):
                shutil.copytree('dist/FileOrganizer', 
                              os.path.join(output_dir, 'FileOrganizer'))
            
            # Create a launcher batch file for easier access
            launcher_content = """@echo off
cd /d "%~dp0"
cd FileOrganizer
start "" "FileOrganizer.exe"
"""
            with open(os.path.join(output_dir, 'Run FileOrganizer.bat'), 'w') as f:
                f.write(launcher_content)
            
            # Create README
            readme = """
╔════════════════════════════════════════════════════════════╗
║           FILE ORGANIZER V2 - READY TO USE!               ║
╚════════════════════════════════════════════════════════════╝

📦 YOUR APP IS HERE!

🚀 TWO WAYS TO RUN:

   METHOD 1 (EASIEST):
   • Double-click "Run FileOrganizer.bat"
   
   METHOD 2:
   • Go into the "FileOrganizer" folder
   • Double-click "FileOrganizer.exe"

⚠️  FIRST TIME OPENING:
   Windows Defender or antivirus may show a warning because
   this is an unsigned app.
   
   If Windows shows "Windows protected your PC":
   • Click "More info"
   • Then click "Run anyway"
   
   If your antivirus blocks it:
   • Add an exception for FileOrganizer.exe
   • Or temporarily disable antivirus to run it once

✅ AFTER THAT:
   The app will run normally!

📁 WHAT IT DOES:
   • Organize messy folders automatically
   • Sort by file type, date, size, or smart categories
   • Preview before organizing
   • Undo if you don't like the result

⚠️  IMPORTANT: Keep all files together!
   The FileOrganizer folder contains necessary files.
   Don't move FileOrganizer.exe by itself.

💡 TIP: You can move the entire "FileOrganizer_Ready_To_Use"
   folder anywhere (Desktop, Documents, etc.)

🐛 TROUBLESHOOTING:
   • If it doesn't open, try running as Administrator
   • Check if antivirus is blocking it
   • Make sure all files in FileOrganizer folder are present

Enjoy organizing your files! 🎉
"""
            with open(os.path.join(output_dir, 'README.txt'), 'w') as f:
                f.write(readme)
            
            print()
            print("=" * 60)
            print("✅ SUCCESS! Your app is ready!")
            print("=" * 60)
            print()
            print(f"📁 Look in the folder: {output_dir}\\")
            print()
            print("👉 EVERYTHING YOU NEED IS IN THAT FOLDER!")
            print()
            print("   • Run FileOrganizer.bat ← Double-click this!")
            print("   • FileOrganizer\\ folder ← Contains the app")
            print("   • README.txt ← Instructions")
            print()
            print("🎁 Share the entire folder with anyone!")
            print()
            print("⚠️  NOTE: Windows may show a security warning")
            print("    the first time. This is normal for unsigned apps.")
            
        else:  # Linux
            print("Building for Linux...")
            subprocess.check_call([
                'pyinstaller',
                '--clean',
                '--windowed',
                '--name=FileOrganizer',
                '--onefile',
                '--noconfirm',
                'file_organizer_v2.py'
            ])
            
            # Move to a better location
            output_dir = "FileOrganizer_Ready_To_Use"
            os.makedirs(output_dir, exist_ok=True)
            
            if os.path.exists('dist/FileOrganizer'):
                shutil.copy2('dist/FileOrganizer', 
                           os.path.join(output_dir, 'FileOrganizer'))
                # Make executable
                os.chmod(os.path.join(output_dir, 'FileOrganizer'), 0o755)
            
            # Create README
            readme = """
╔════════════════════════════════════════════════════════════╗
║           FILE ORGANIZER V2 - READY TO USE!               ║
╚════════════════════════════════════════════════════════════╝

📦 YOUR APP IS HERE: FileOrganizer

🚀 HOW TO USE:
   Option 1: Double-click FileOrganizer
   Option 2: Run in terminal: ./FileOrganizer

📁 WHAT IT DOES:
   • Organize messy folders automatically
   • Sort by file type, date, size, or smart categories
   • Preview before organizing
   • Undo if you don't like the result

Enjoy organizing your files! 🎉
"""
            with open(os.path.join(output_dir, 'README.txt'), 'w') as f:
                f.write(readme)
            
            print()
            print("=" * 60)
            print("✅ SUCCESS! Your app is ready!")
            print("=" * 60)
            print()
            print(f"📁 Look in the folder: {output_dir}/")
            print()
            print("👉 EVERYTHING YOU NEED IS IN THAT FOLDER!")
            print()
            print("   • FileOrganizer ← This is your app!")
            print("   • README.txt ← Instructions for users")
        
    except subprocess.CalledProcessError as e:
        print()
        print("❌ Build failed!")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print()
        print("❌ Unexpected error!")
        print(f"Error: {e}")
        return False
    
    print()
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = create_executable()
    if not success:
        input("\nPress Enter to exit...")
        sys.exit(1)
    else:
        input("\nPress Enter to exit...")