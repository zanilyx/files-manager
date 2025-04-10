# Files Manager 🗃️🔧

**Files Manager** is a sleek and powerful Tkinter-based desktop application for Windows that lets you:

- 📎 Merge multiple file types (PDFs, images, PowerPoints, Word files, etc.) into a single PDF.
- 🐍 Convert `.py` (Python scripts) into standalone `.exe` files.
- 💻 Compile `.c` (C source files) into `.exe` executables using GCC.
- 🧹 Clean up unnecessary files after conversion.
- ⏱️ Get detailed time stats for operations.
- ✅ Optional auto-deletion of source files after merging.
- 🌙 Simple dropdown UI to switch between different tools.

---

## 📦 Features

| Feature                  | Description                                                 |
|--------------------------|-------------------------------------------------------------|
| 📁 File Merger           | Select multiple files (PDF, PNG, JPG, PPTX, DOCX, etc.) and merge into one PDF. |
| 🔄 .py to .exe Converter | Uses PyInstaller to convert Python files to EXEs and cleans up spec and build files. |
| 🔧 .c to .exe Compiler   | Uses GCC (MinGW) to compile C code into Windows executables. |
| 🧽 Clean Output          | Final `.exe` is placed alongside the source file. |
| ⏳ Time Feedback         | Shows how long each operation takes. |
| 🗑️ Optional Cleanup     | Checkbox to delete originals after merging. |
| 🎨 Clean UI             | Tkinter-based UI with dropdowns and themed buttons. |

---

## 📸 Screenshots

> Coming soon...

---

## 🔧 Requirements

- Python 3.10+
- GCC (for compiling `.c` files) – install via [MinGW](https://www.mingw-w64.org/)
- PyInstaller – install via pip:
  ```bash
  pip install pyinstaller
