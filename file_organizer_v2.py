import os
import shutil
import json
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer v2")
        self.root.geometry("900x650")

        self.selected_folder = None
        self.preview_data = {}
        self.history_file = Path.home() / ".file_organizer_history.json"
        self.last_operation = None

        # --- Top frame: folder selection ---
        top_frame = tk.Frame(root)
        top_frame.pack(fill="x", padx=10, pady=10)

        self.folder_label = tk.Label(top_frame, text="No folder selected", anchor="w")
        self.folder_label.pack(side="left", expand=True, fill="x")

        browse_btn = tk.Button(top_frame, text="Choose Folder", command=self.choose_folder)
        browse_btn.pack(side="right", padx=5)

        undo_btn = tk.Button(top_frame, text="Undo Last", command=self.undo_last, state="disabled")
        undo_btn.pack(side="right")
        self.undo_btn = undo_btn

        # --- Middle frame: split view ---
        middle_frame = tk.Frame(root)
        middle_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left side: current files
        left_frame = tk.Frame(middle_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        tk.Label(left_frame, text="Current Files", font=("Arial", 10, "bold")).pack()
        
        self.files_listbox = tk.Listbox(left_frame)
        self.files_listbox.pack(side="left", fill="both", expand=True)

        scrollbar1 = tk.Scrollbar(left_frame, command=self.files_listbox.yview)
        scrollbar1.pack(side="right", fill="y")
        self.files_listbox.config(yscrollcommand=scrollbar1.set)

        # Right side: preview tree
        right_frame = tk.Frame(middle_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        tk.Label(right_frame, text="Preview (After Organization)", font=("Arial", 10, "bold")).pack()
        
        self.preview_tree = ttk.Treeview(right_frame)
        self.preview_tree.pack(side="left", fill="both", expand=True)

        scrollbar2 = tk.Scrollbar(right_frame, command=self.preview_tree.yview)
        scrollbar2.pack(side="right", fill="y")
        self.preview_tree.config(yscrollcommand=scrollbar2.set)

        # --- Options frame ---
        options_frame = tk.LabelFrame(root, text="Options", padx=10, pady=10)
        options_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Mode selector
        tk.Label(options_frame, text="Organize by:").grid(row=0, column=0, sticky="w", padx=5)
        self.mode_var = tk.StringVar(value="File Type")
        mode_options = ["File Type", "Modified Date (YYYY-MM)", "File Size", "Smart Categories"]
        mode_menu = ttk.Combobox(options_frame, textvariable=self.mode_var, values=mode_options, state="readonly", width=20)
        mode_menu.grid(row=0, column=1, padx=5)
        mode_menu.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

        # Action mode
        tk.Label(options_frame, text="Action:").grid(row=0, column=2, sticky="w", padx=5)
        self.action_var = tk.StringVar(value="Move")
        action_menu = ttk.Combobox(options_frame, textvariable=self.action_var, values=["Move", "Copy"], state="readonly", width=10)
        action_menu.grid(row=0, column=3, padx=5)
        action_menu.bind("<<ComboboxSelected>>", lambda e: self.update_preview())

        # Include subfolders
        self.recursive_var = tk.BooleanVar(value=False)
        recursive_cb = tk.Checkbutton(options_frame, text="Include subfolders", variable=self.recursive_var, command=self.update_preview)
        recursive_cb.grid(row=0, column=4, padx=10)

        # --- Bottom frame: actions ---
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        self.organize_btn = tk.Button(bottom_frame, text="Organize Now", command=self.organize, bg="#FF5722", fg="white", font=("Arial", 11, "bold"), activebackground="#E64A19", activeforeground="white", padx=20, pady=5)
        self.organize_btn.pack(side="left", padx=5)

        self.status_label = tk.Label(bottom_frame, text="Ready", anchor="w")
        self.status_label.pack(side="left", padx=10)

        self.progress = ttk.Progressbar(bottom_frame, mode='determinate', length=200)
        self.progress.pack(side="right", padx=5)

        # Load last operation for undo
        self.load_last_operation()

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        self.selected_folder = Path(folder)
        self.folder_label.config(text=str(self.selected_folder))
        self.refresh_file_list()
        self.update_preview()

    def refresh_file_list(self):
        """List files in the selected folder."""
        self.files_listbox.delete(0, tk.END)
        if not self.selected_folder:
            return

        files = self.get_all_files()
        for file_path in files:
            rel_path = file_path.relative_to(self.selected_folder)
            self.files_listbox.insert(tk.END, str(rel_path))

    def get_all_files(self):
        """Get all files based on recursive option."""
        if not self.selected_folder:
            return []
        
        files = []
        if self.recursive_var.get():
            for item in self.selected_folder.rglob("*"):
                if item.is_file():
                    files.append(item)
        else:
            for item in self.selected_folder.iterdir():
                if item.is_file():
                    files.append(item)
        return files

    def update_preview(self):
        """Generate and display preview of organization."""
        self.preview_tree.delete(*self.preview_tree.get_children())
        
        if not self.selected_folder:
            return

        mode = self.mode_var.get()
        files = self.get_all_files()
        
        # Group files by target folder
        self.preview_data = {}
        
        for file_path in files:
            target_folder = self.determine_target_folder(file_path, mode)
            if target_folder not in self.preview_data:
                self.preview_data[target_folder] = []
            self.preview_data[target_folder].append(file_path)

        # Display in tree
        for folder_name in sorted(self.preview_data.keys()):
            file_list = self.preview_data[folder_name]
            folder_id = self.preview_tree.insert("", "end", text=f"📁 {folder_name} ({len(file_list)} files)", open=True)
            
            for file_path in sorted(file_list):
                self.preview_tree.insert(folder_id, "end", text=f"  📄 {file_path.name}")

        total_files = sum(len(files) for files in self.preview_data.values())
        self.status_label.config(text=f"Preview: {total_files} files → {len(self.preview_data)} folders")

    def determine_target_folder(self, file_path, mode):
        """Determine which folder a file should go to based on mode."""
        if mode == "File Type":
            ext = file_path.suffix.lower().strip(".")
            return ext if ext else "no_extension"
        
        elif mode == "Modified Date (YYYY-MM)":
            try:
                mtime = file_path.stat().st_mtime
                dt = datetime.fromtimestamp(mtime)
                return f"{dt.year}-{dt.month:02d}"
            except:
                return "unknown_date"
        
        elif mode == "File Size":
            try:
                size = file_path.stat().st_size
                if size < 1024 * 1024:  # < 1MB
                    return "Small (< 1MB)"
                elif size < 10 * 1024 * 1024:  # < 10MB
                    return "Medium (1-10MB)"
                elif size < 100 * 1024 * 1024:  # < 100MB
                    return "Large (10-100MB)"
                else:
                    return "Huge (> 100MB)"
            except:
                return "Unknown Size"
        
        elif mode == "Smart Categories":
            ext = file_path.suffix.lower().strip(".")
            
            images = ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp", "ico"]
            videos = ["mp4", "avi", "mkv", "mov", "wmv", "flv", "webm"]
            audio = ["mp3", "wav", "flac", "aac", "ogg", "wma", "m4a"]
            documents = ["pdf", "doc", "docx", "txt", "odt", "rtf", "tex"]
            spreadsheets = ["xls", "xlsx", "csv", "ods"]
            presentations = ["ppt", "pptx", "odp"]
            archives = ["zip", "rar", "7z", "tar", "gz", "bz2"]
            code = ["py", "js", "html", "css", "java", "cpp", "c", "h", "go", "rs", "php", "rb"]
            
            if ext in images:
                return "Images"
            elif ext in videos:
                return "Videos"
            elif ext in audio:
                return "Audio"
            elif ext in documents:
                return "Documents"
            elif ext in spreadsheets:
                return "Spreadsheets"
            elif ext in presentations:
                return "Presentations"
            elif ext in archives:
                return "Archives"
            elif ext in code:
                return "Code"
            elif ext == "":
                return "No Extension"
            else:
                return "Other"
        
        return "Unknown"

    def organize(self):
        """Execute the organization with confirmation."""
        if not self.selected_folder:
            messagebox.showwarning("No Folder", "Please choose a folder first.")
            return

        if not self.preview_data:
            self.update_preview()

        total_files = sum(len(files) for files in self.preview_data.values())
        action = self.action_var.get().lower()
        
        msg = f"This will {action} {total_files} files into {len(self.preview_data)} folders.\n\nContinue?"
        if not messagebox.askyesno("Confirm Organization", msg):
            return

        # Perform organization
        operation_log = []
        moved_count = 0
        self.progress["maximum"] = total_files
        self.progress["value"] = 0

        for folder_name, file_list in self.preview_data.items():
            target_folder = self.selected_folder / folder_name
            target_folder.mkdir(exist_ok=True)

            for file_path in file_list:
                target_path = target_folder / file_path.name
                
                # Handle duplicates
                counter = 1
                original_target = target_path
                while target_path.exists():
                    stem = original_target.stem
                    suffix = original_target.suffix
                    target_path = original_target.parent / f"{stem}_{counter}{suffix}"
                    counter += 1

                try:
                    if action == "move":
                        shutil.move(str(file_path), str(target_path))
                    else:  # copy
                        shutil.copy2(str(file_path), str(target_path))
                    
                    operation_log.append({
                        "action": action,
                        "source": str(file_path),
                        "destination": str(target_path)
                    })
                    moved_count += 1
                except Exception as e:
                    print(f"Error {action}ing {file_path}: {e}")

                self.progress["value"] += 1
                self.root.update_idletasks()

        # Save operation for undo
        if action == "move":
            self.save_operation(operation_log)
            self.undo_btn.config(state="normal")

        self.status_label.config(text=f"Completed: {moved_count} files {action}d")
        self.refresh_file_list()
        self.update_preview()
        messagebox.showinfo("Done", f"Successfully {action}d {moved_count} files!")

    def save_operation(self, operation_log):
        """Save the last operation for undo."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "operations": operation_log
        }
        try:
            with open(self.history_file, 'w') as f:
                json.dump(data, f)
            self.last_operation = data
        except Exception as e:
            print(f"Error saving history: {e}")

    def load_last_operation(self):
        """Load the last operation if available."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.last_operation = json.load(f)
                    self.undo_btn.config(state="normal")
        except Exception as e:
            print(f"Error loading history: {e}")

    def undo_last(self):
        """Undo the last organization operation."""
        if not self.last_operation:
            messagebox.showinfo("No History", "No operation to undo.")
            return

        msg = "This will undo the last organization and restore files to their original locations.\n\nContinue?"
        if not messagebox.askyesno("Confirm Undo", msg):
            return

        operations = self.last_operation.get("operations", [])
        restored_count = 0
        self.progress["maximum"] = len(operations)
        self.progress["value"] = 0

        for op in reversed(operations):  # Reverse to avoid conflicts
            if op["action"] == "move":
                dest = Path(op["destination"])
                src = Path(op["source"])
                
                if dest.exists():
                    try:
                        # Ensure source directory exists
                        src.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(dest), str(src))
                        restored_count += 1
                    except Exception as e:
                        print(f"Error restoring {dest}: {e}")

            self.progress["value"] += 1
            self.root.update_idletasks()

        # Clean up empty folders
        if self.selected_folder:
            for item in self.selected_folder.iterdir():
                if item.is_dir():
                    try:
                        if not any(item.iterdir()):
                            item.rmdir()
                    except:
                        pass

        # Clear history
        try:
            self.history_file.unlink()
        except:
            pass
        
        self.last_operation = None
        self.undo_btn.config(state="disabled")
        
        self.status_label.config(text=f"Restored {restored_count} files")
        self.refresh_file_list()
        self.update_preview()
        messagebox.showinfo("Undo Complete", f"Successfully restored {restored_count} files!")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()