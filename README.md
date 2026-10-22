# 🛡️ FileGuard — Digital File Integrity & Tampering Detector

FileGuard is a cybersecurity tool built with **Python** and **Streamlit** that lets you
verify whether a file has been changed since it was first recorded. It does this by
computing the **SHA-256 cryptographic hash** of any uploaded file and comparing it against
a previously saved reference hash. The entire process runs locally in your browser session —
no file content is transmitted, stored permanently, or executed.

---

## Problem Statement

Files shared over networks, stored in cloud drives, or passed between systems are
vulnerable to silent modification — whether from accidental corruption, software bugs,
or deliberate tampering. Without a reliable way to verify a file's integrity, there is no
simple method to confirm that the copy you received is identical to the original.

Existing tools for hash verification are often command-line-only and unfamiliar to
beginners. FileGuard aims to make the process accessible through a clean browser interface
while maintaining the correctness and safety properties required for real use.

---

## Objectives

1. Compute the SHA-256 hash of any uploaded file entirely within the browser session.
2. Allow the user to record a hash as a trusted original reference.
3. Export the reference hash as a structured JSON record for use in future sessions.
4. Import a previously exported JSON record and validate its structure and hash format.
5. Compare the current hash of a file against the original reference and display a clear
   pass/fail result with a character-level diff when hashes differ.
6. Provide a downloadable plain-text verification report suitable for audit trails.
7. Explain what a match and a mismatch mean in plain language, including the limitations
   of hash-based verification.

---

## Features

| Feature | Description |
|---|---|
| SHA-256 hash computation | Calculates the full 64-character hex digest of any uploaded file, processed in 64 KB chunks |
| Original reference recording | Saves the hash and filename in the browser session with a UTC timestamp |
| JSON export | Downloads a structured `.json` verification record for safe keeping |
| JSON import & validation | Loads a previously exported record; validates schema, tool sentinel, and hash format |
| File verification | Compares the current hash against the recorded or imported reference |
| Colour-coded verdict banner | Shows **✅ File Unchanged** or **⚠️ File Modified** with a plain-English sub-heading |
| Character-level hash diff | When hashes differ, highlights the exact positions that changed in red on a teal background |
| Side-by-side hash comparison | Shows original and current hashes in selectable, monospace text areas |
| Verification report download | Exports a plain-text `.txt` report with all comparison details and a UTC timestamp |
| Visual step-progress tracker | A pill-row beneath the header shows Step 1 → Step 2 → Export, updating live as you complete each step |
| Live sidebar dashboard | Shows session status (recorded filename, timestamp, hash) and workflow steps at a glance |
| Safety explanations | Explains what a mismatch does and does not mean; includes a trust reminder |
| Local-only processing | No data is transmitted, stored permanently, or executed |
| 10 MB file size limit | Guards against accidental uploads of very large files |

---

## Technologies Used

| Layer | Technology |
|---|---|
| Language | Python 3.9 or newer |
| Web framework | [Streamlit](https://streamlit.io/) ≥ 1.32.0 |
| Hashing | `hashlib` — Python standard library |
| File I/O | `io` — Python standard library |
| JSON handling | `json` — Python standard library |
| Input validation | `re` — Python standard library |
| Timestamps | `datetime` — Python standard library |

No third-party libraries beyond Streamlit are required.

---

## Project Structure

```
FileGuard/
├── app.py                ← Main Streamlit application (v4.0) + self-test suite
├── requirements.txt      ← Python package dependencies
├── README.md             ← This file
└── PROJECT_REPORT.md     ← College-style project report
```

> `app.py` contains a built-in self-test suite at the bottom under
> `if __name__ == "__main__":`. Running `python app.py` executes 70 automated
> checks on all helper functions without needing a browser.

---

## Prerequisites

- **Python 3.9 or newer** — download from [python.org](https://www.python.org/downloads/)
- **pip** — bundled with Python; used to install packages
- A modern web browser (Chrome, Firefox, Edge, or Safari)

> **Why Python 3.9?**
> The code uses `tuple[bool, str]` as a return-type annotation (lowercase built-in
> generics), which requires Python 3.9+. It also uses the walrus operator (`:=`), which
> requires Python 3.8+. Python 3.9 satisfies both.

---

## Installation

### Step 1 — Get the project files

**Option A — Clone with Git**

```bash
git clone https://github.com/your-username/fileguard.git
cd fileguard
```

**Option B — Download ZIP**

Download and extract the ZIP archive, then open a terminal inside the `FileGuard` folder.

---

### Step 2 — Create a virtual environment (recommended)

A virtual environment keeps the project's dependencies separate from your system Python
installation and avoids version conflicts with other projects.

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt once the environment is
active. Run all subsequent commands in the same terminal window.

---

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

This installs only Streamlit. All other modules used by the app — `hashlib`, `io`,
`json`, `re`, `datetime` — are part of the Python standard library and require no
installation.

---

### Step 4 — Run the application

```bash
streamlit run app.py
```

Streamlit will print a local URL (usually `http://localhost:8501`) and open it in your
default browser automatically. If it does not open, copy the URL and paste it manually.

To stop the app, press `Ctrl + C` in the terminal.

---

### Step 5 — Run the built-in self-tests (optional)

```bash
python app.py
```

This runs 70 automated checks on all helper functions directly from `app.py`.
No browser is opened. Streamlit prints some harmless "bare mode" warnings to
stderr — ignore them. The test result appears in stdout and ends with:

```
============================================================
  70 passed  /  0 failed  /  70 total
============================================================
```

---

## How to Use

The app is divided into two main steps, shown on the main page. A visual step-progress
tracker at the top of the page shows which step is currently active and updates
automatically as you complete each one.

---

### Step 1 — Record the Original Hash

1. Open the app in your browser.
2. In the **Step 1** card, click **Browse files** (or drag and drop a file) to upload
   the file you want to protect.
3. FileGuard reads the file in memory and computes its SHA-256 hash. The 64-character
   hex digest is displayed in a selectable text area — click inside it, press
   **Ctrl+A** then **Ctrl+C** to copy it.
4. Click **📌 Record as original reference**. The hash, filename, and UTC timestamp are
   saved in the current browser session. The sidebar and the step tracker both update to
   confirm the reference is active.
5. To save the reference for use in a future browser session, expand the
   **Active reference hash** panel below the uploader and click
   **⬇️ Download verification record (.json)**. Store this `.json` file somewhere safe
   (see Safety Considerations for guidance).

---

### Step 2 — Verify a File

**If you are continuing in the same session as Step 1:**

1. Scroll to the **Step 2** card. The status pill confirms that a reference is already
   loaded from Step 1.
2. Under **Option B** (right column), upload the file you want to check.
3. FileGuard computes the file's current SHA-256 hash and compares it with the reference.
4. A verdict banner shows either:
   - **✅ File Unchanged** — the hashes match exactly; every byte is identical.
   - **⚠️ File Modified** — the hashes differ; the file's contents have changed.
5. Below the verdict, a four-column metadata row shows the filename, file size, UTC
   verification time, and result.
6. In the **Hash Comparison** section:
   - If the hashes match, both are shown in teal monospace text areas.
   - If the hashes differ, the current hash is shown as a character-level diff: positions
     that match the original are teal, and positions that differ are red with a dark
     background highlight.
7. Read the **What does this mean?** panel for a plain-English explanation.
8. Click **⬇️ Download verification report (.txt)** to save a plain-text audit report.
   The button label includes the result (`UNCHANGED` or `MODIFIED`) so it is easy to
   identify in your downloads folder.

**If you are starting a new session and have a saved JSON record:**

1. In the **Step 2** card, use **Option A** (left column) to upload the `.json` file
   you exported in a previous session.
2. FileGuard validates the record's required fields, tool identifier, and the
   64-character hex format of the stored hash before accepting it. The file is parsed
   as text only — it is never executed.
3. A success message confirms the original filename and recording timestamp.
4. Proceed with **Option B** as described above.

---

## How SHA-256 Verification Works

SHA-256 is a one-way cryptographic hash function. It takes any input — a document, an
image, an executable — and produces a fixed 64-character hexadecimal string called a
**digest** or **hash**.

```
Any file  →  SHA-256  →  64-character hex string
                          e3b0c44298fc1c14...9afbf4c8996fb924
```

**Key properties:**

- **Deterministic** — the same file bytes always produce the same hash.
- **Avalanche effect** — changing even one byte produces a completely different hash.
- **One-way** — it is not possible to reconstruct the original file from its hash.
- **Collision-resistant** — it is computationally infeasible to find two different files
  that produce the same hash.

A concrete example (shown in the app's SHA-256 explainer section):

```
Input: "Hello, World!"
SHA-256: dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f

Input: "Hello, World?"  ← only the last character changed
SHA-256: f16c3bb0532537acd5b2e418f2b1235b29181e35cffee7cc29d84de4a1d62e4d
```

The entire 64-character digest changes from just one character difference — this is the
avalanche effect.

FileGuard uses Python's standard-library `hashlib.sha256()`, reading the file in 64 KB
chunks to handle files up to the 10 MB limit without loading the entire file into memory
at once.

**What a match means:** every byte of the file is identical to the version that was
hashed when the reference was recorded.

**What a mismatch means:** the file's contents have changed since the reference was
recorded. The cause could be an intentional edit, accidental corruption during transfer,
uploading a different version by mistake, or deliberate tampering. A mismatch alone does
not identify which of these occurred.

---

## Safety Considerations and Limitations

| Consideration | How FileGuard addresses it |
|---|---|
| Uploaded files are never executed | Files are read as raw bytes only; no `exec`, `subprocess`, or shell call is made anywhere in the code |
| File contents are not stored permanently | Data lives only in the Streamlit in-memory session; closing or refreshing the browser clears everything |
| Filenames are not trusted for comparison | The comparison is always between two SHA-256 hex digests computed from file contents, never between filename strings |
| Imported JSON records are validated | All five required fields, the `"FileGuard"` tool sentinel, and the 64-character lowercase hex format are verified before the record is used |
| A mismatch is not proof of malice | The app lists four alternative explanations and does not claim that tampering occurred |
| A match is not proof of safety | If the original file already contained malware, a matching hash means the file is unchanged — not that it is safe |
| The JSON record itself must be protected | If an attacker can modify both the file and the JSON record, the comparison provides no protection. Store records in encrypted storage, a signed commit, or another tamper-evident location |
| 10 MB upload limit | Files above 10 MB are rejected with a clear error message before any processing begins |

---

## Example Testing Scenarios

The following scenarios describe ways to manually verify that each feature works as
expected. They use any ordinary file you already have on your computer.

---

### Scenario 1 — Confirming an unchanged file

1. Upload a text file (for example `notes.txt`) in Step 1 and click
   **📌 Record as original reference**.
2. In Step 2 Option B, upload the **exact same file** again without modifying it.
3. Expected result: green **✅ File Unchanged** banner; both hash boxes show identical
   teal text; the four-column metadata row shows `✅ Unchanged`.

---

### Scenario 2 — Detecting a modified file

1. Upload a text file in Step 1 and record its hash.
2. Open the file in any text editor, add or remove a single character, and save it.
3. Upload the modified file in Step 2 Option B.
4. Expected result: red **⚠️ File Modified** banner; the **Hash Comparison** section
   shows the current hash as a character-level diff where positions that changed are
   highlighted in red against the teal original characters.

---

### Scenario 3 — JSON record export and re-import

1. Upload a file in Step 1, record its hash, expand the **Active reference hash** panel,
   and click **⬇️ Download verification record (.json)**.
2. Refresh the browser to start a new session (this clears the in-memory reference).
3. In Step 2 Option A, upload the `.json` record you downloaded.
4. Expected result: a green success message showing the original filename and recording
   timestamp; the reference hash is now active.
5. Upload the same original file in Option B.
6. Expected result: **✅ File Unchanged**.

---

### Scenario 4 — Invalid or tampered JSON record

1. Create a plain text file named `fake.json` containing `{ "hello": "world" }`.
2. Upload it in Step 2 Option A.
3. Expected result: a red error message listing the missing required fields.

---

### Scenario 5 — Verification report download

1. Complete any verification (match or mismatch).
2. Click the **⬇️ Download verification report (.txt)** button. The button label includes
   the result (`UNCHANGED` or `MODIFIED`).
3. Open the downloaded `.txt` file in any text editor.
4. Expected result: a structured plain-text report containing the reference filename,
   reference SHA-256 hash, current file SHA-256 hash, UTC verification timestamp, and
   a `Hashes match: YES / NO` line followed by a safety note about what a mismatch means.

---

### Scenario 6 — Running the built-in self-tests

1. With the virtual environment active, run:
   ```bash
   python app.py
   ```
2. Expected result: all 70 tests pass with `0 failed` in the stdout output.
   Streamlit's harmless "bare mode" warnings on stderr can be ignored.

---

## Future Enhancements

The following improvements are not currently implemented but represent natural next steps:

- **Verification history log** — display a table of all comparisons performed in the
  current session, exportable as CSV.
- **Multiple file comparison** — allow batch hashing and comparison of several files at
  once.
- **PDF report export** — generate a formatted PDF version of the verification report.
- **Hash algorithm choice** — support MD5 and SHA-1 for compatibility with legacy systems
  (with appropriate warnings about their weaknesses relative to SHA-256).
- **Command-line mode** — a companion `cli.py` script for scripted or automated
  verification workflows that do not require a browser.
- **Digital signature support** — sign the JSON record with a private key so that any
  tampering with the record itself can be detected independently of the file comparison.

---

## License

This project is released for educational purposes. You are free to adapt it for
coursework, internship submissions, or personal learning projects.
