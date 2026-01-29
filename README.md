# 🛡️ No Metadata — Photo Metadata Remover

A small, offline desktop tool (Tkinter + Pillow) that **strips all metadata** from images for privacy.  
Drag & drop or add files/folders, click **Remove Metadata**, and cleaned images are saved to a `No Metadata` folder next to the app.

---

## ✨ Features
- ✅ Dark-themed GUI (Tkinter)
- ✅ Drag & drop support (uses `tkinterdnd2` when bundled)
- ✅ Batch processing (many images at once)
- ✅ Outputs to `No Metadata` folder next to the program
- ✅ Duplicate output naming: `name(1).jpg`, `name(2).jpg`, ...
- ✅ After processing the input list clears automatically
- ✅ `Clear List` removes the **last** added item (one at a time)

---

## 📦 Prerequisites
You only need these installed in your build environment (the final packaged app can be fully offline):

- Python 3.8+
- Pillow
- tkinterdnd2 (the script assumes this is present at runtime)
- Pyinstaller (for building your executable file)

---

## Language Used:

<p align="left">
  <img alt="Python" src="https://skillicons.dev/icons?i=python" width="40" height="40"/>
  <img alt="Tkinter" src="https://skillicons.dev/icons?i=tk" width="40" height="40"/>
  <img alt="PyInstaller" src="https://skillicons.dev/icons?i=pyinstaller" width="40" height="40"/>
  <img alt="YAML" src="https://skillicons.dev/icons?i=yaml" width="40" height="40"/>
  <img alt="Text" src="https://skillicons.dev/icons?i=txt" width="40" height="40"/>
</p>

---

##  🏗  Build Your Own EXE

Open a terminal in the project folder and run:

```bash
# Navigate to project folder
cd path/to/project

# Create EXE with icon and version info
pyinstaller --windowed --icon=icon.ico --version-file=file_version_info.txt "nometadata.py"
