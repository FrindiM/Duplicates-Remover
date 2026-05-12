# 🗂️ Duplicate File Remover

A lightweight desktop application for finding and removing duplicate files from any folder on your computer. Built with Python and Tkinter — no extra libraries required.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 Smart scanning | Detects duplicates using SHA-256 content hashing — not just filenames |
| 📁 Recursive search | Scans all subfolders automatically |
| 📊 Progress bar | Live progress updates while scanning |
| ☑️ Selective delete | Choose exactly which duplicates to remove |
| 📐 File size info | Shows size of each duplicate and total space reclaimable |
| ✅ Confirm before delete | Safety dialog before any file is permanently removed |
| ⚡ Non-blocking UI | Scanning runs in a background thread — the app stays responsive |

---

## 📋 Requirements

- **Python 3.8+** (uses the walrus operator `:=`)
- **Tkinter** — included with most Python installations

### Check your Python version

```bash
python --version
# or
python3 --version
```

### Install Tkinter (if missing)

**Ubuntu / Debian:**
```bash
sudo apt install python3-tk
```

**macOS (Homebrew):**
```bash
brew install python-tk
```

**Windows:** Tkinter is bundled with the official Python installer from [python.org](https://python.org).

---

## 🚀 Installation & Running

### 1. Clone the repository

```bash
git clone https://github.com/FrindiM/Duplicates-Remover.git
cd Duplicates-Remover
```

### 2. Run the application

```bash
python duplicate.py
# or, on some systems:
python3 duplicate.py
```

No additional packages need to be installed.

---

## 🖥️ How to Use

### Step 1 — Select a folder

Click **Browse…** and choose the folder you want to scan. All subfolders will be included automatically.

### Step 2 — Scan for duplicates

Click **🔍 Scan**. A progress bar shows the scanning status. When finished, all duplicate files appear in the results table.

> **How detection works:** Every file is read and hashed with SHA-256. Two files are considered duplicates only when their content is byte-for-byte identical — not just when they share a name. The *first* occurrence found is kept as the "original"; subsequent identical files are listed as "duplicates."

### Step 3 — Review results

The table shows three columns:

| Column | Description |
|---|---|
| **✓** | Checkbox — tick files you want to delete |
| **Duplicate File** | Full path of the duplicate copy |
| **Original File** | Full path of the file that will be kept |
| **Size** | Size of the duplicate file |

The status bar at the bottom shows the total number of duplicates, total reclaimable space, and how many files are currently selected.

### Step 4 — Delete selected duplicates

1. Tick the checkboxes of the files you want to remove (use **Select All** / **Deselect All** for convenience).
2. Click **🗑 Delete Selected**.
3. Confirm the deletion in the dialog box.

> ⚠️ **Warning:** Deletion is permanent. Files are removed directly — they are **not** sent to the Recycle Bin / Trash. Make sure you review your selection carefully before confirming.

---

## 📸 Screenshot

```
┌─────────────────────────────────────────────────────────────────┐
│  Folder: [C:\Users\You\Downloads          ] [Browse…] [🔍 Scan]  │
│  [████████████████████████░░░░] Scanning… 142/200               │
│  ┌──┬──────────────────────────┬──────────────────────┬──────┐  │
│  │✓ │ Duplicate File           │ Original File        │ Size │  │
│  ├──┼──────────────────────────┼──────────────────────┼──────┤  │
│  │☑ │ Downloads\photo(1).jpg   │ Downloads\photo.jpg  │ 2.4MB│  │
│  │☐ │ Downloads\report_v2.pdf  │ Docs\report_v2.pdf   │ 512KB│  │
│  └──┴──────────────────────────┴──────────────────────┴──────┘  │
│  2 duplicate(s) │ 2.9 MB reclaimable │ 1 selected (2.4 MB)      │
│           [Select All] [Deselect All]  [🗑 Delete Selected]      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔒 Safety Notes

- The application **never deletes the original** — only the duplicate copy is removed.
- Always **back up important data** before running any file-cleanup tool.
- For extra safety, test on a small, non-critical folder first.

---

## 🛠️ Project Structure

```
Duplicates-Remover/
└── duplicate.py   # Main application (all-in-one)
```

---

## 🤝 Contributing

Pull requests are welcome! Some ideas for future enhancements:

- Move duplicates to Trash instead of permanent delete
- Export results to CSV
- Filter by file type (images only, documents only, …)
- Dark mode

---

## 📄 License

This project is open-source. Feel free to use and modify it.
