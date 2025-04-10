import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import tempfile
import time
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF
import comtypes.client
import subprocess
import threading
import shutil


SUPPORTED_TYPES = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.jpg', '.jpeg', '.png', '.bmp', '.gif']

class FilesManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📁 Files Manager")
        self.root.geometry("650x550")
        self.root.resizable(False, False)

        self.mode = tk.StringVar(value="File Merger")
        self.delete_after_merge = tk.BooleanVar(value=False)

        self.file_list = []
        self.temp_dir = tempfile.mkdtemp()

        self.build_ui()

    def build_ui(self):
        # Dropdown to switch mode
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Select Feature: ", font=("Segoe UI", 10)).pack(side="left")
        feature_menu = ttk.Combobox(top_frame, textvariable=self.mode, values=["File Merger", ".py to .exe", ".c to .exe"], state="readonly", width=20)
        feature_menu.pack(side="left", padx=10)
        feature_menu.bind("<<ComboboxSelected>>", self.switch_mode)

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, pady=10)

        self.status_label = tk.Label(self.root, text="", font=("Segoe UI", 9, "italic"))
        self.status_label.pack()

        self.switch_mode()

    def switch_mode(self, event=None):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.file_list.clear()

        if self.mode.get() == "File Merger":
            self.build_file_merger_ui()
        elif self.mode.get() == ".py to .exe":
            self.build_py_to_exe_ui()
        elif self.mode.get() == ".c to .exe":
            self.build_c_to_exe_ui()

    ##########################
    # FILE MERGER COMPONENTS
    ##########################

    def build_file_merger_ui(self):
        title = tk.Label(self.main_frame, text="🧩 Merge Files into a PDF", font=("Segoe UI", 14, "bold"))
        title.pack()

        self.file_box = tk.Listbox(self.main_frame, font=("Segoe UI", 10), height=10)
        self.file_box.pack(fill="both", expand=True, padx=20, pady=5)

        btns = tk.Frame(self.main_frame)
        btns.pack()

        tk.Button(btns, text="Add Files", command=self.add_files).grid(row=0, column=0, padx=5)
        tk.Button(btns, text="Remove Selected", command=self.remove_selected).grid(row=0, column=1, padx=5)
        tk.Button(btns, text="Clear All", command=self.clear_all).grid(row=0, column=2, padx=5)

        self.del_check = tk.Checkbutton(self.main_frame, text="Delete originals after merging", variable=self.delete_after_merge)
        self.del_check.pack(pady=5)

        tk.Button(self.main_frame, text="Merge to PDF", bg="#2196F3", fg="white", font=("Segoe UI", 11, "bold"),
                  command=lambda: threading.Thread(target=self.merge_all).start()).pack(pady=10)

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Supported Files", "*.*")])
        for f in files:
            if f not in self.file_list and os.path.splitext(f)[1].lower() in SUPPORTED_TYPES:
                self.file_list.append(f)
                self.file_box.insert("end", os.path.basename(f))
            else:
                self.set_status(f"Unsupported or duplicate: {os.path.basename(f)}")

    def remove_selected(self):
        selected = self.file_box.curselection()
        for i in reversed(selected):
            del self.file_list[i]
            self.file_box.delete(i)

    def clear_all(self):
        self.file_list.clear()
        self.file_box.delete(0, "end")

    def set_status(self, msg):
        self.status_label.config(text=msg)
        self.root.update_idletasks()

    def convert_office(self, file, output_pdf):
        ext = os.path.splitext(file)[1].lower()
        app = None
        try:
            if ext in ['.doc', '.docx']:
                app = comtypes.client.CreateObject("Word.Application")
                doc = app.Documents.Open(file)
                doc.SaveAs(output_pdf, FileFormat=17)
                doc.Close()
            elif ext in ['.xls', '.xlsx']:
                app = comtypes.client.CreateObject("Excel.Application")
                doc = app.Workbooks.Open(file)
                doc.ExportAsFixedFormat(0, output_pdf)
                doc.Close()
            elif ext in ['.ppt', '.pptx']:
                app = comtypes.client.CreateObject("PowerPoint.Application")
                doc = app.Presentations.Open(file)
                doc.SaveAs(output_pdf, 32)
                doc.Close()
        finally:
            if app:
                app.Quit()

    def convert_image(self, file, output_pdf):
        img = Image.open(file)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(output_pdf, "PDF")

    def convert_txt(self, file, output_pdf):
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
        img = Image.new("RGB", (595, 842), color="white")
        d = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        d.multiline_text((40, 40), text, fill=(0, 0, 0), font=font)
        img.save(output_pdf, "PDF")

    def convert_to_pdf(self, file):
        ext = os.path.splitext(file)[1].lower()
        output_pdf = os.path.join(self.temp_dir, os.path.basename(file) + ".pdf")

        if ext == '.pdf':
            return file
        elif ext in ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
            self.convert_office(file, output_pdf)
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            self.convert_image(file, output_pdf)
        elif ext == '.txt':
            self.convert_txt(file, output_pdf)
        else:
            raise Exception(f"Unsupported file type: {ext}")

        return output_pdf

    def merge_all(self):
        if not self.file_list:
            messagebox.showwarning("No Files", "Please add files first.")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not output_path:
            return

        self.set_status("Starting merge...")
        start_time = time.time()

        pdfs = []
        try:
            for i, file in enumerate(self.file_list):
                self.set_status(f"Converting: {os.path.basename(file)}")
                pdf = self.convert_to_pdf(file)
                pdfs.append(pdf)

            self.set_status("Merging PDFs...")
            merged = fitz.open()
            for p in pdfs:
                with fitz.open(p) as doc:
                    merged.insert_pdf(doc)
            merged.save(output_path)

            if self.delete_after_merge.get():
                for f in self.file_list:
                    try:
                        os.remove(f)
                    except Exception:
                        pass

            elapsed = round(time.time() - start_time, 2)
            self.set_status(f"Done ✅ Time taken: {elapsed} seconds")
            messagebox.showinfo("Success", f"Merged PDF saved!\nTime taken: {elapsed}s")
        except Exception as e:
            self.set_status("Failed ❌")
            messagebox.showerror("Error", str(e))
        finally:
            # Clean up temporary files
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = tempfile.mkdtemp()

    #############################
    # PY TO EXE UI
    #############################

    def build_py_to_exe_ui(self):
        title = tk.Label(self.main_frame, text="🐍 .py to .exe Converter", font=("Segoe UI", 14, "bold"))
        title.pack(pady=10)

        self.py_path = tk.StringVar()

        tk.Button(self.main_frame, text="Select .py File", command=self.select_py_file).pack()
        tk.Label(self.main_frame, textvariable=self.py_path, wraplength=500).pack(pady=5)

        tk.Button(self.main_frame, text="Convert to .exe", bg="#4CAF50", fg="white", command=self.convert_py_to_exe).pack(pady=10)

    def select_py_file(self):
        path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        self.py_path.set(path)

    def convert_py_to_exe(self):
        py_file = self.py_path.get()
        if not py_file:
            messagebox.showwarning("Select File", "Please select a Python file first.")
            return

        try:
            start_time = time.time()
            subprocess.run(["pyinstaller", "--onefile", py_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            base_name = os.path.splitext(os.path.basename(py_file))[0]
            exe_name = f"{base_name}.exe"

            exe_path = os.path.join("dist", exe_name)
            final_path = os.path.join(os.path.dirname(py_file), exe_name)

            if os.path.exists(exe_path):
                shutil.move(exe_path, final_path)

            # Clean up build, dist, and spec file
            shutil.rmtree("dist", ignore_errors=True)
            shutil.rmtree("build", ignore_errors=True)
            spec_file = f"{base_name}.spec"
            if os.path.exists(spec_file):
                os.remove(spec_file)

            end_time = time.time()
            messagebox.showinfo("Success", f"Converted {os.path.basename(py_file)} to EXE in {end_time - start_time:.2f} seconds.\nSaved at:\n{final_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert {os.path.basename(py_file)}:\n{str(e)}")


    #############################
    # C TO EXE UI
    #############################

    def build_c_to_exe_ui(self):
        title = tk.Label(self.main_frame, text="🛠️ .c to .exe Converter", font=("Segoe UI", 14, "bold"))
        title.pack(pady=10)

        self.c_path = tk.StringVar()

        tk.Button(self.main_frame, text="Select .c File", command=self.select_c_file).pack()
        tk.Label(self.main_frame, textvariable=self.c_path, wraplength=500).pack(pady=5)

        tk.Button(self.main_frame, text="Compile to .exe", bg="#4CAF50", fg="white", command=self.compile_c_to_exe).pack(pady=10)

    def select_c_file(self):
        path = filedialog.askopenfilename(filetypes=[("C files", "*.c")])
        self.c_path.set(path)

    def compile_c_to_exe(self):
        path = self.c_path.get()
        if not path:
            messagebox.showwarning("Select File", "Please select a C file.")
            return

        exe_path = os.path.splitext(path)[0] + ".exe"
        try:
            subprocess.run(f"gcc \"{path}\" -o \"{exe_path}\"", shell=True)
            messagebox.showinfo("Success", f"Compiled to: {exe_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    app = FilesManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()