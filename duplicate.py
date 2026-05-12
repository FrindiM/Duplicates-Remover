import os
import hashlib
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# ── Utility ──────────────────────────────────────────────────────────────────

def hash_file(filepath):
    """Return SHA-256 hex-digest of a file, or None on error."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None


def human_size(n_bytes):
    """Convert byte count to human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} PB"


def find_duplicates(folder_path, progress_callback=None):
    """
    Walk *folder_path* recursively and return a list of
    (duplicate_path, original_path, size_bytes) tuples.
    progress_callback(current, total) is called if provided.
    """
    # Collect all files first so we know the total count for the progress bar.
    all_files = []
    for root, _, files in os.walk(folder_path):
        for fname in files:
            all_files.append(os.path.join(root, fname))

    hashes = {}
    duplicates = []

    for idx, filepath in enumerate(all_files, 1):
        if progress_callback:
            progress_callback(idx, len(all_files))

        file_hash = hash_file(filepath)
        if file_hash is None:
            continue

        if file_hash in hashes:
            try:
                size = os.path.getsize(filepath)
            except OSError:
                size = 0
            duplicates.append((filepath, hashes[file_hash], size))
        else:
            hashes[file_hash] = filepath

    return duplicates


# ── GUI ───────────────────────────────────────────────────────────────────────

class DuplicateRemoverApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Duplicate File Remover")
        self.geometry("860x520")
        self.resizable(True, True)
        self.configure(bg="#f5f5f5")

        self._duplicates = []   # cache: list of (dup, orig, size)
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Top bar: folder selection ──────────────────────────────────────
        top = tk.Frame(self, bg="#f5f5f5")
        top.pack(fill=tk.X, padx=12, pady=(12, 4))

        tk.Label(top, text="Folder:", bg="#f5f5f5", font=("Segoe UI", 10)).pack(side=tk.LEFT)

        self.entry_path = tk.Entry(top, width=55, font=("Segoe UI", 10))
        self.entry_path.pack(side=tk.LEFT, padx=(6, 4))

        tk.Button(top, text="Browse…", command=self._browse,
                  font=("Segoe UI", 10), bg="#4a90d9", fg="white",
                  relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(top, text="🔍  Scan", command=self._start_scan,
                  font=("Segoe UI", 10, "bold"), bg="#27ae60", fg="white",
                  relief=tk.FLAT, padx=10).pack(side=tk.LEFT)

        # ── Progress bar ───────────────────────────────────────────────────
        prog_frame = tk.Frame(self, bg="#f5f5f5")
        prog_frame.pack(fill=tk.X, padx=12, pady=(0, 4))

        self.progress_var = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(prog_frame, variable=self.progress_var,
                                           maximum=100, length=600)
        self.progressbar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.lbl_status = tk.Label(prog_frame, text="Ready", bg="#f5f5f5",
                                   font=("Segoe UI", 9), fg="#555", width=24,
                                   anchor="w")
        self.lbl_status.pack(side=tk.LEFT)

        # ── Results table ──────────────────────────────────────────────────
        cols = ("select", "duplicate", "original", "size")
        self.tree = ttk.Treeview(self, columns=cols, show="headings",
                                 selectmode="extended")
        self.tree.heading("select",    text="✓")
        self.tree.heading("duplicate", text="Duplicate File")
        self.tree.heading("original",  text="Original File")
        self.tree.heading("size",      text="Size")
        self.tree.column("select",    width=30,  anchor="center", stretch=False)
        self.tree.column("duplicate", width=340, anchor="w")
        self.tree.column("original",  width=340, anchor="w")
        self.tree.column("size",      width=80,  anchor="e", stretch=False)

        vsb = ttk.Scrollbar(self, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(12, 0), pady=4)
        vsb.pack(side=tk.LEFT, fill=tk.Y, pady=4)
        hsb.pack(side=tk.BOTTOM, fill=tk.X, padx=12)

        self.tree.bind("<Button-1>", self._on_row_click)

        # ── Bottom bar: summary + action buttons ───────────────────────────
        bottom = tk.Frame(self, bg="#f5f5f5")
        bottom.pack(fill=tk.X, padx=12, pady=(4, 10))

        self.lbl_summary = tk.Label(bottom, text="No scan yet.",
                                    bg="#f5f5f5", font=("Segoe UI", 9), fg="#333")
        self.lbl_summary.pack(side=tk.LEFT)

        btn_frame = tk.Frame(bottom, bg="#f5f5f5")
        btn_frame.pack(side=tk.RIGHT)

        tk.Button(btn_frame, text="Select All",   command=self._select_all,
                  font=("Segoe UI", 9), relief=tk.FLAT, bg="#bbb", padx=6).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame, text="Deselect All", command=self._deselect_all,
                  font=("Segoe UI", 9), relief=tk.FLAT, bg="#bbb", padx=6).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_frame, text="🗑  Delete Selected",
                  command=self._delete_selected,
                  font=("Segoe UI", 10, "bold"), bg="#e74c3c", fg="white",
                  relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=(6, 0))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, folder)

    def _set_ui_busy(self, busy: bool):
        state = tk.DISABLED if busy else tk.NORMAL
        for w in self.winfo_children():
            try:
                w.configure(state=state)
            except tk.TclError:
                pass

    def _update_summary(self):
        checked = [iid for iid in self.tree.get_children()
                   if self.tree.set(iid, "select") == "☑"]
        total = len(self._duplicates)
        total_size = sum(d[2] for d in self._duplicates)
        sel_size = sum(self._duplicates[self.tree.get_children().index(iid)][2]
                       for iid in checked
                       if iid in self.tree.get_children())

        self.lbl_summary.config(
            text=f"{total} duplicate(s) found  |  {human_size(total_size)} reclaimable  "
                 f"|  {len(checked)} selected ({human_size(sel_size)})"
        )

    # ── Checkbox toggle in column 0 ───────────────────────────────────────────

    def _on_row_click(self, event):
        col = self.tree.identify_column(event.x)
        if col == "#1":           # "select" column
            row = self.tree.identify_row(event.y)
            if row:
                cur = self.tree.set(row, "select")
                self.tree.set(row, "select", "☑" if cur == "☐" else "☐")
                self._update_summary()

    def _select_all(self):
        for iid in self.tree.get_children():
            self.tree.set(iid, "select", "☑")
        self._update_summary()

    def _deselect_all(self):
        for iid in self.tree.get_children():
            self.tree.set(iid, "select", "☐")
        self._update_summary()

    # ── Scan (runs in background thread) ──────────────────────────────────────

    def _start_scan(self):
        folder = self.entry_path.get().strip()
        if not folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return
        if not os.path.isdir(folder):
            messagebox.showerror("Error", "The selected path is not a valid folder.")
            return

        self.tree.delete(*self.tree.get_children())
        self._duplicates = []
        self.progress_var.set(0)
        self.lbl_status.config(text="Scanning…")
        self.lbl_summary.config(text="")
        self._set_ui_busy(True)

        threading.Thread(target=self._scan_worker, args=(folder,), daemon=True).start()

    def _scan_worker(self, folder):
        def progress(cur, total):
            pct = (cur / total * 100) if total else 100
            self.progress_var.set(pct)
            self.lbl_status.config(text=f"Scanning… {cur}/{total}")

        duplicates = find_duplicates(folder, progress_callback=progress)
        self.after(0, self._on_scan_done, duplicates)

    def _on_scan_done(self, duplicates):
        self._duplicates = duplicates
        self._set_ui_busy(False)
        self.progress_var.set(100)

        if not duplicates:
            self.lbl_status.config(text="Done — no duplicates found.")
            self.lbl_summary.config(text="No duplicates found.")
            messagebox.showinfo("Scan complete", "No duplicate files were found.")
            return

        for dup, orig, size in duplicates:
            self.tree.insert("", tk.END,
                             values=("☐", dup, orig, human_size(size)))

        self.lbl_status.config(text=f"Done — {len(duplicates)} duplicate(s)")
        self._update_summary()

    # ── Delete ─────────────────────────────────────────────────────────────────

    def _delete_selected(self):
        all_iids = self.tree.get_children()
        selected = [iid for iid in all_iids
                    if self.tree.set(iid, "select") == "☑"]

        if not selected:
            messagebox.showwarning("Nothing selected",
                                   "Tick the checkbox (✓ column) for each file you want to delete.")
            return

        total_size = sum(
            self._duplicates[all_iids.index(iid)][2]
            for iid in selected
        )

        confirm = messagebox.askyesno(
            "Confirm deletion",
            f"Permanently delete {len(selected)} file(s)?\n"
            f"This will free up {human_size(total_size)}.\n\n"
            "This action cannot be undone."
        )
        if not confirm:
            return

        errors = []
        deleted = 0
        for iid in selected:
            filepath = self.tree.set(iid, "duplicate")
            try:
                os.remove(filepath)
                self.tree.delete(iid)
                deleted += 1
            except Exception as e:
                errors.append(f"{filepath}: {e}")

        # Rebuild internal cache to stay in sync with the tree
        remaining_iids = self.tree.get_children()
        self._duplicates = [
            self._duplicates[list(self.tree.get_children()).index(iid)]
            for iid in remaining_iids
            if iid in remaining_iids
        ]

        msg = f"{deleted} file(s) deleted successfully."
        if errors:
            msg += f"\n\n{len(errors)} error(s):\n" + "\n".join(errors)
            messagebox.showwarning("Done with errors", msg)
        else:
            messagebox.showinfo("Done", msg)

        self._update_summary()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = DuplicateRemoverApp()
    app.mainloop()
