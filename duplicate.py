import os
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def hash_file(filepath):
    """Menghasilkan hash SHA-256 dari sebuah file."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        return None

def find_duplicates(folder_path):
    """Mencari file duplikat berdasarkan hash."""
    hashes = {}
    duplicates = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            filepath = os.path.join(root, file)
            file_hash = hash_file(filepath)
            if file_hash:
                if file_hash in hashes:
                    duplicates.append((filepath, hashes[file_hash]))
                else:
                    hashes[file_hash] = filepath
    
    return duplicates

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, folder_selected)

def search_duplicates():
    folder_path = entry_path.get()
    if not folder_path:
        messagebox.showerror("Error", "Pilih folder terlebih dahulu!")
        return
    
    duplicates = find_duplicates(folder_path)
    
    tree.delete(*tree.get_children())
    
    if duplicates:
        for dup in duplicates:
            tree.insert("", tk.END, values=(dup[0], dup[1]))
        messagebox.showinfo("Hasil", f"Ditemukan {len(duplicates)} file duplikat.")
    else:
        messagebox.showinfo("Hasil", "Tidak ada file duplikat yang ditemukan.")

def delete_duplicates():
    selected_items = tree.get_children()
    if not selected_items:
        messagebox.showerror("Error", "Tidak ada file duplikat untuk dihapus!")
        return
    
    for item in selected_items:
        filepath = tree.item(item, "values")[0]
        try:
            os.remove(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghapus {filepath}: {e}")
    
    search_duplicates()
    messagebox.showinfo("Selesai", "File duplikat berhasil dihapus.")

# GUI dengan Tkinter
root = tk.Tk()
root.title("Penghapus File Duplikat")
root.geometry("700x400")

frame = tk.Frame(root)
frame.pack(pady=10)

entry_path = tk.Entry(frame, width=50)
entry_path.pack(side=tk.LEFT, padx=5)
btn_browse = tk.Button(frame, text="Pilih Folder", command=browse_folder)
btn_browse.pack(side=tk.LEFT)

btn_search = tk.Button(root, text="Cari Duplikat", command=search_duplicates)
btn_search.pack(pady=5)

columns = ("Duplikat", "Asli")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.heading("Duplikat", text="File Duplikat")
tree.heading("Asli", text="File Asli")
tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

btn_delete = tk.Button(root, text="Hapus Duplikat", command=delete_duplicates)
btn_delete.pack(pady=5)

root.mainloop()
