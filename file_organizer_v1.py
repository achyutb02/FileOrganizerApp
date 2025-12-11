import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer")
        self.root.geometry("700x500")

        self.selected_folder = None

        # --- Top frame: folder selection ---
        top_frame = tk.Frame(root)
        top_frame.pack(fill="x", padx=10, pady=10)

        self.folder_label = tk.Label(top_frame, text="No folder selected", anchor="w")
        self.folder_label.pack(side="left", expand=True, fill="x")

        browse_btn = tk.Button(top_frame, text="Choose Folder", command=self.choose_folder)
        browse_btn.pack(side="right")

        # --- Middle frame: file list and options ---
        middle_frame = tk.Frame(root)
        middle_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.files_listbox = tk.Listbox(middle_frame)
        self.files_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(middle_frame, command=self.files_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.files_listbox.config(yscrollcommand=scrollbar.set)

        # --- Bottom frame: actions ---
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        organize_btn = tk.Button(bottom_frame, text="Organize by File Type", command=self.organize_by_type)
        organize_btn.pack(side="left")

        self.status_label = tk.Label(bottom_frame, text="Ready", anchor="w")
        self.status_label.pack(side="left", padx=10)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        self.selected_folder = Path(folder)
        self.folder_label.config(text=str(self.selected_folder))
        self.refresh_file_list()

    def refresh_file_list(self):
        """List files in the selected folder (non-recursive for MVP)."""
        self.files_listbox.delete(0, tk.END)
        if not self.selected_folder:
            return

        for item in self.selected_folder.iterdir():
            if item.is_file():
                self.files_listbox.insert(tk.END, item.name)

    def organize_by_type(self):
        if not self.selected_folder:
            messagebox.showwarning("No Folder", "Please choose a folder first.")
            return

        moved_count = 0

        for item in self.selected_folder.iterdir():
            if item.is_file():
                ext = item.suffix.lower().strip(".")  # e.g. ".jpg" -> "jpg"
                if ext == "":
                    ext_folder = "no_extension"
                else:
                    ext_folder = ext

                target_folder = self.selected_folder / ext_folder
                target_folder.mkdir(exist_ok=True)

                target_path = target_folder / item.name
                try:
                    shutil.move(str(item), str(target_path))
                    moved_count += 1
                except Exception as e:
                    print(f"Error moving {item}: {e}")

        self.status_label.config(text=f"Moved {moved_count} files")
        self.refresh_file_list()
        messagebox.showinfo("Done", f"Organized {moved_count} files by type.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()
