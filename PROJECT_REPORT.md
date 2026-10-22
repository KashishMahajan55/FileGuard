# PROJECT REPORT

---

## Title Page

| Field | Detail |
|---|---|
| **Project Title** | FileGuard — Digital File Integrity & Tampering Detector |
| **Student Name** | *(your name)* |
| **Roll Number** | *(your roll number)* |
| **Course** | B.Tech Computer Science and Engineering |
| **Subject** | Cybersecurity / Information Security |
| **Department** | *(your department)* |
| **College** | *(your college name)* |
| **Project Guide** | *(guide's name and designation)* |
| **Submission Date** | *(date of submission)* |
| **Version** | 4.0 |

---

## Abstract

FileGuard is a browser-based file integrity verification tool built with Python and
Streamlit. It computes the SHA-256 cryptographic hash of any uploaded file, allows the
user to record that hash as a trusted reference, and compares a file's current hash
against the reference at any later time to determine whether the file has been changed.

The application runs entirely on the user's local machine. No file content, hash, or
metadata is transmitted to any external server. Files are never written to disk and are
never executed.

The tool addresses a practical gap: existing hash verification utilities are either
command-line tools unfamiliar to beginners or heavyweight enterprise systems. FileGuard
provides the same underlying verification method — SHA-256 comparison — through a clean,
step-by-step browser interface that requires no technical background to operate.

Key capabilities include SHA-256 hash computation, original reference recording,
structured JSON export and import for cross-session verification, side-by-side hash
comparison, colour-coded pass/fail verdicts, and a downloadable plain-text verification
report. The design deliberately avoids over-claiming: the application explains in plain
language what a hash match and mismatch each do and do not mean.

---

## 1. Introduction

### 1.1 Background

Digital files are the primary medium through which information is created, shared, and
stored. A document, a software installer, a database export, or a configuration file may
pass through email servers, cloud storage platforms, USB drives, and network file shares
before reaching its intended recipient. At every step, the file is vulnerable to
unintended or malicious modification.

Traditional antivirus software detects known malware signatures, but it does not answer a
simpler, equally important question: *"Is this the exact file I originally had?"*
Cryptographic hash functions provide a mathematically precise answer to that question.

### 1.2 Motivation

A first-year engineering or cybersecurity student typically learns about SHA-256 from
textbooks but has no accessible tool to interact with it hands-on without using a terminal
command. FileGuard was developed to bridge that gap — to make a real security primitive
usable by anyone with a browser.

### 1.3 Document Structure

This report is organised as follows. Section 2 states the problem. Section 3 sets the
objectives. Section 4 defines the scope. Section 5 reviews the existing approach and the
proposed solution. Sections 6 and 7 cover requirements and technologies. Sections 8 and 9
present the system design and SHA-256 explanation. Section 10 describes the implementation
of each project file. Section 11 lists all features. Section 12 contains the testing plan.
Section 13 discusses results. Sections 14 through 17 cover advantages, limitations, future
work, and the conclusion. References are listed at the end.

---

## 2. Problem Statement

Files shared over networks, stored in cloud drives, or passed between systems are
vulnerable to silent modification. Causes include:

- **Transmission errors** during network transfer or storage media degradation.
- **Software bugs** in editors, converters, or synchronisation tools.
- **Deliberate tampering** by an attacker who has access to the file at any point in its
  journey from sender to receiver.

Without an independent integrity check, there is no reliable way to confirm that the copy
of a file you have today is byte-for-byte identical to the version that was originally
created or distributed.

Existing tools that solve this problem fall into two categories:

1. **Command-line utilities** (`sha256sum` on Linux/macOS, `certutil -hashfile` on
   Windows) — effective but inaccessible to users who are not comfortable with terminals.
2. **Enterprise FIM tools** (Tripwire, AIDE, osquery) — powerful but complex, requiring
   installation, configuration, and system-level access.

There is no lightweight, beginner-friendly, browser-based tool that covers the complete
workflow: compute a hash, save it as a reference, and verify a file against that reference
in a later session.

---

## 3. Objectives

1. Compute the SHA-256 hash of any uploaded file entirely within the user's browser
   session, without transmitting file contents to any server.
2. Allow the user to record a computed hash as a trusted original reference, with a UTC
   timestamp and the original filename.
3. Export the recorded reference as a structured JSON file that can be stored securely and
   used in a future session.
4. Import a previously exported JSON record and validate its structure and SHA-256 format
   before using it as a reference.
5. Compare the current hash of a file against the active reference and display a clear,
   colour-coded pass/fail verdict.
6. Show both hashes side-by-side in selectable text areas so the user can inspect them
   directly.
7. Generate a downloadable plain-text verification report containing the filenames, both
   hashes, the verification timestamp, and the result.
8. Explain the meaning and limitations of hash-based verification in plain language within
   the application itself.
9. Enforce safety controls: size limits, no file execution, no permanent storage, and
   honest messaging about what a hash match does and does not guarantee.

---

## 4. Scope of the Project

**In scope:**

- SHA-256 hash computation for any file up to 10 MB in size.
- Recording a reference hash in the current browser session.
- Exporting and importing a structured JSON verification record.
- Comparing a file's current hash against a reference hash.
- Displaying a verdict, a side-by-side hash comparison, and a plain-text report.
- Running entirely on the user's local machine with no network communication.
- Supporting any operating system that can run Python 3.9 and a modern web browser.

**Out of scope:**

- Antivirus scanning, malware detection, or any analysis of file contents beyond hashing.
- Permanent storage of files, hashes, or user data of any kind.
- Multi-user or networked deployment.
- Automated or scheduled integrity monitoring.
- PDF report generation (identified as a future enhancement).
- Verification of more than one file at a time in a single session.

---

## 5. Existing Approach and Proposed Solution

### 5.1 Existing Approach

The standard method for manual file integrity verification is to use a command-line tool
to compute a hash and compare it visually or with a script:

```
# Linux / macOS
sha256sum report.pdf

# Windows
certutil -hashfile report.pdf SHA256
```

This approach is correct and widely used in professional and academic settings. However,
it requires the user to:

- Open a terminal and type a command with exact syntax.
- Copy and save the output manually.
- Re-run the command later and compare the two strings by eye.
- Know what a hash is and what a mismatch means.

For a student, a non-technical professional, or anyone unfamiliar with a terminal, this
workflow is a barrier.

### 5.2 Proposed Solution

FileGuard wraps the same underlying primitive — SHA-256 via Python's `hashlib` — in a
browser interface that guides the user through each step:

1. **Step 1**: Upload a file, see the hash, click one button to record it.
2. **Export**: Download the reference as a JSON file for safe keeping.
3. **Step 2**: Upload the file again (or load the saved record), see both hashes
   side-by-side, and receive an immediate verdict.

The comparison is performed entirely in Python memory. The result is explained in plain
language. The limitations are stated honestly. No command-line knowledge is required.

---

## 6. Software and Hardware Requirements

### 6.1 Software Requirements

| Component | Requirement |
|---|---|
| Operating system | Windows 10+, macOS 11+, or any modern Linux distribution |
| Python | Version 3.9 or newer |
| pip | Bundled with Python; used to install Streamlit |
| Streamlit | Version 1.32.0 or newer (installed via `requirements.txt`) |
| Web browser | Chrome, Firefox, Edge, or Safari (any modern browser) |

> **Note on Python version:** The code uses the walrus operator (`:=`) introduced in
> Python 3.8, and lowercase built-in generics in type annotations (e.g. `tuple[bool, str]`)
> introduced in Python 3.9. Python 3.9 is therefore the minimum compatible version.

### 6.2 Hardware Requirements

| Component | Minimum |
|---|---|
| Processor | Any processor capable of running Python 3.9 |
| RAM | 256 MB available to the Python process |
| Disk space | Approximately 200 MB for Python, Streamlit, and their dependencies |
| Network | Not required; the application runs entirely offline |

The memory requirement is deliberately conservative. The application reads uploaded files
into a `BytesIO` buffer in memory. With the 10 MB file size limit, peak memory usage
during hashing is under 20 MB for the file data itself.

---

## 7. Technologies Used

### 7.1 Python 3.9

Python is the implementation language. It was chosen for its readable syntax, extensive
standard library, and widespread use in cybersecurity education. No compiled or low-level
code is required.

### 7.2 Streamlit (≥ 1.32.0)

Streamlit is a Python framework that converts a regular Python script into an interactive
web application. It handles all HTML rendering, widget state management, and browser
communication. FileGuard uses the following Streamlit components:

- `st.file_uploader` — accepts uploaded files as in-memory byte streams.
- `st.text_area` — displays hashes in selectable, monospace text boxes.
- `st.metric` — displays file metadata in styled cards.
- `st.columns` — arranges content in side-by-side columns.
- `st.download_button` — offers JSON records and text reports for download.
- `st.session_state` — stores the recorded hash, filename, and timestamp across reruns.
- `st.expander` — collapses the reference-hash panel to reduce visual clutter.
- `st.sidebar` — shows a live dashboard of the current session status.

### 7.3 hashlib (Python standard library)

`hashlib` provides access to a range of cryptographic hash functions. FileGuard uses
`hashlib.sha256()`, which produces a 256-bit (32-byte) digest represented as a 64-character
lowercase hexadecimal string. It is part of the Python standard library and requires no
installation.

### 7.4 Other Standard Library Modules

| Module | Purpose in this project |
|---|---|
| `io` | Wraps raw bytes in a `BytesIO` stream for chunked reading |
| `json` | Serialises and parses the verification record |
| `re` | Validates that a SHA-256 field is exactly 64 lowercase hex characters |
| `datetime` | Generates UTC timestamps for record creation and verification events |

---

## 8. System Design and Working Methodology

### 8.1 Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   User's Browser                     │
│                                                      │
│   Streamlit front-end (rendered from app.py)         │
│                                                      │
│   ┌──────────────┐      ┌───────────────────────┐   │
│   │   Step 1     │      │        Step 2          │   │
│   │  (Record)    │      │  (Verify / Compare)    │   │
│   └──────┬───────┘      └──────────┬────────────┘   │
│          │                         │                 │
└──────────┼─────────────────────────┼─────────────────┘
           │                         │
           ▼                         ▼
┌─────────────────────────────────────────────────────┐
│              Python process  (app.py)                │
│                                                      │
│   compute_sha256()  ←  hashlib.sha256()              │
│   validate_record() ←  re.fullmatch()                │
│   build_record()    →  json.dumps()                  │
│   build_verification_report()  →  plain text string  │
│                                                      │
│   st.session_state  ←  hash, filename, timestamp     │
└─────────────────────────────────────────────────────┘
```

All components run in a single Python process on the user's machine. There are no database
connections, no external API calls, and no file system writes.

### 8.2 Data Flow — Recording a Reference Hash

1. The user selects a file using the `st.file_uploader` widget in Step 1.
2. Streamlit reads the file into memory as a bytes object.
3. The size is checked: if it exceeds 10 MB or is zero, an error or warning is shown and
   processing stops.
4. `compute_sha256()` creates a `hashlib.sha256()` object, wraps the bytes in a
   `BytesIO` stream, and reads it in 64 KB chunks, updating the hash object with each
   chunk. It returns the 64-character hex digest.
5. The hash is displayed in a `st.text_area` widget.
6. If the user clicks "Record as original reference", the hash, filename, and current UTC
   timestamp are stored in `st.session_state`.
7. The sidebar updates immediately to show the active reference.

### 8.3 Data Flow — JSON Export

1. The user expands the "Active reference hash" panel and clicks the download button.
2. `build_record()` assembles a Python dictionary containing the schema version, tool
   name, original filename, SHA-256 hash, and recorded-at timestamp.
3. `json.dumps()` serialises it with indentation.
4. Streamlit's `st.download_button` offers the resulting bytes as a `.json` file
   download in the browser.

### 8.4 Data Flow — Verification

1. The user optionally uploads a saved `.json` record in Step 2 Option A.
2. If uploaded, the file is decoded as UTF-8 and parsed with `json.loads()`. It is never
   executed.
3. `validate_record()` checks that all required fields are present, that the `"tool"`
   field equals `"FileGuard"`, and that the `"sha256"` value matches the pattern
   `[0-9a-f]{64}` via `re.fullmatch()`. If validation fails, an error is shown.
4. If no JSON record is uploaded, the session-state reference (from Step 1) is used.
5. The user uploads the file to verify in Option B.
6. `compute_sha256()` computes the current hash of that file.
7. The two hashes are compared with a simple string equality check (`==`).
8. A colour-coded verdict banner is shown: teal for a match, red for a mismatch.
9. Both hashes are displayed side-by-side in `st.text_area` widgets. The current-file
   hash area uses teal text on a match and red text on a mismatch.
10. `build_verification_report()` assembles a plain-text report string.
11. `st.download_button` offers the report as a `.txt` file download.

### 8.5 Session State Management

Streamlit reruns the entire script on every user interaction. To persist the recorded
hash across reruns, three values are stored in `st.session_state`:

| Key | Type | Content |
|---|---|---|
| `recorded_hash` | `str` or `None` | 64-character SHA-256 hex digest |
| `recorded_filename` | `str` or `None` | Name of the file when the hash was recorded |
| `recorded_at` | `str` or `None` | UTC timestamp in ISO 8601 format |

These values are cleared when the user clicks "Clear" or refreshes the browser tab.

### 8.6 Security Controls

| Threat | Control implemented in the code |
|---|---|
| Uploaded file executed | Files are only read with `.read()` into `bytes`; no `exec`, `import`, `subprocess`, or shell call is made anywhere in `app.py` |
| Data exfiltration | Streamlit runs on `localhost`; no HTTP requests to external services are made |
| Oversized file causing memory pressure | `MAX_FILE_SIZE_BYTES` (10 MB) is checked before `compute_sha256()` is called |
| Empty file | `size == 0` is checked before hashing |
| Crafted JSON record bypassing validation | `validate_record()` checks required keys, the `"tool"` sentinel, and the 64-char hex format |
| Hash match falsely implying file safety | The UI explicitly states that a match confirms byte-for-byte identity only, not the absence of malware |
| Record tampering going unnoticed | A trust-reminder panel explains that the record is only reliable if it has itself been protected |

---

## 9. SHA-256 Hashing Explanation

### 9.1 What SHA-256 Is

SHA-256 (Secure Hash Algorithm, 256-bit output) is a member of the SHA-2 family of
cryptographic hash functions, standardised by the National Institute of Standards and
Technology (NIST) in FIPS PUB 180-4. It takes an input of arbitrary length and produces
a fixed 256-bit (32-byte) output, conventionally written as a 64-character lowercase
hexadecimal string.

### 9.2 Key Properties

**Deterministic.** The same sequence of bytes always produces the same hash. If you hash
the same file twice, on the same machine or on different machines, you will always get the
same 64-character string.

**Avalanche effect.** A single bit change in the input — even changing one character in a
text file — results in a completely different hash output. There is no incremental or
partial match between the hashes of two similar files.

**Pre-image resistance.** Given a hash value, it is computationally infeasible to find
any input that produces that hash. The hash cannot be "reversed" to recover the original
file.

**Collision resistance.** It is computationally infeasible to find two different inputs
that produce the same hash output. This means each file has, for all practical purposes,
a unique hash.

### 9.3 How FileGuard Uses SHA-256

```python
def compute_sha256(file_bytes: bytes) -> str:
    h = hashlib.sha256()
    stream = io.BytesIO(file_bytes)
    while chunk := stream.read(65536):   # 64 KB chunks
        h.update(chunk)
    return h.hexdigest()
```

A `hashlib.sha256()` object maintains an internal state. Each call to `.update(chunk)`
feeds more bytes into the hash computation. When all bytes have been processed,
`.hexdigest()` finalises the computation and returns the 64-character string. Reading in
chunks rather than all at once makes the function compatible with the 10 MB limit without
loading unnecessary data structures.

### 9.4 Example

The following examples use the exact same values displayed in the app's SHA-256 explainer
section and verified by the project's automated test suite:

```
Input: "Hello, World!"   (13 bytes, no newline)
SHA-256: dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f

Input: "Hello, World?"   (last character changed from ! to ?)
SHA-256: f16c3bb0532537acd5b2e418f2b1235b29181e35cffee7cc29d84de4a1d62e4d
```

Every single character of the hash is different despite only one character changing in the
input — this is the avalanche effect.

### 9.5 What a Hash Match and Mismatch Each Mean

**Match:** Every byte of the file presented for verification is identical to every byte
of the file that was hashed when the reference was recorded. The file has not been altered,
corrupted, or substituted.

**Mismatch:** The file's byte content differs from what was recorded. Possible causes
include an intentional edit, accidental corruption during transfer or storage, uploading a
different version of the file, or malicious tampering. A mismatch does not by itself
identify the cause.

**Important limitation:** A hash match confirms identity only. If the original file
already contained malicious content, its hash would still match after being copied
unchanged. FileGuard is not an antivirus tool.

---

## 10. Implementation and Description of the Four Project Files

### 10.1 `app.py` — Main Application (v4.0)

`app.py` is the single Python file that contains the entire application. It is structured
in the following order:

**Imports and constants**

```python
import hashlib, io, json, re
from datetime import datetime, timezone
import streamlit as st

MAX_FILE_SIZE_MB    = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
RECORD_SCHEMA_VERSION = "1"
```

Only `streamlit` is an external package. All other imports are Python standard library.
`RECORD_SCHEMA_VERSION` is a string constant embedded in every exported JSON record; it
can be incremented if the record format changes in a future version.

**Page configuration**

```python
st.set_page_config(
    page_title="FileGuard – File Integrity Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)
```

`layout="wide"` uses the full browser width. `initial_sidebar_state="expanded"` keeps
the dashboard visible on load. This must be the first Streamlit call in the script.

**Custom CSS**

Injected via `st.markdown(..., unsafe_allow_html=True)`. Styles the background
(`#0d1b2a` navy), headings (`#00c9a7` teal), step cards, status pills, verdict banners,
hash text areas, and file uploader drop zone. All styles are scoped to the application's
own CSS classes and Streamlit's known `data-testid` attributes.

**Helper functions**

| Function | Signature | Purpose |
|---|---|---|
| `compute_sha256` | `(bytes) -> str` | Computes and returns the 64-char SHA-256 hex digest using 64 KB chunked reads |
| `format_file_size` | `(int) -> str` | Converts a byte count to a human-readable B / KB / MB string |
| `is_valid_sha256` | `(str) -> bool` | Returns `True` only if the input matches `[0-9a-f]{64}` exactly |
| `build_record` | `(str, str, str) -> dict` | Assembles the JSON record dictionary from filename, hash, and timestamp |
| `validate_record` | `(dict) -> tuple[bool, str]` | Checks all required fields, the tool sentinel, and the hash format |
| `now_utc` | `() -> str` | Returns the current UTC time as an ISO 8601 string |
| `build_verification_report` | `(str, str, str, str, str, str, str) -> str` | Assembles the plain-text verification report |

**Session-state initialisation**

```python
for key, default in [
    ("recorded_hash",     None),
    ("recorded_filename", None),
    ("recorded_at",       None),
]:
    if key not in st.session_state:
        st.session_state[key] = default
```

Initialises the three session-state keys on first load without overwriting existing values
on subsequent reruns.

**Sidebar dashboard**

Rendered inside `with st.sidebar:`. Displays the three-step workflow overview and a live
status panel that shows either a "Reference recorded" pill with the filename, timestamp,
and hash, or a "No reference recorded yet" pill when the session is empty.

**Step 1 — Record the Original Hash**

- File uploader (`source_uploader`): accepts any file type up to 10 MB.
- Size and emptiness checks before calling `compute_sha256()`.
- Hash displayed in a `st.text_area` with monospace styling.
- Three `st.metric` cards show filename, size, and algorithm.
- "Record as original reference" button writes to `st.session_state` and calls
  `st.rerun()` to refresh the sidebar immediately.
- An `st.expander` shows the current reference hash, allows JSON export via
  `st.download_button`, and provides a "Clear" button.

**Step 2 — Verify a File**

- Option A: JSON record uploader (`json_uploader`), limited to `.json` files.
  Parses with `json.loads()`, validates with `validate_record()`, and displays
  a success message with the imported metadata.
- Reference resolution: imported JSON takes priority over session-state.
- A status pill shows which reference is active, or warns that none is available.
- Option B: file uploader (`verify_uploader`), any file type.
  After size checks and reference availability check, calls `compute_sha256()`.
  Displays the verdict banner, four metric cards, side-by-side hash text areas,
  a plain-language explanation, a trust reminder, and a report download button.

**SHA-256 explainer**

An `st.expander` at the bottom of the page (collapsed by default) contains a static
explanation of SHA-256 properties.

---

### 10.2 `requirements.txt`

```
# FileGuard – Python dependencies
# Install with:  pip install -r requirements.txt
#
# All other imports used by app.py (hashlib, io, json, re, datetime) are
# part of the Python standard library and do not need to be listed here.

streamlit>=1.32.0
```

Streamlit is the only external dependency. The minimum version `1.32.0` was the stable
release available when the project was developed; later versions are compatible. No other
packages are required or listed.

---

### 10.3 `README.md`

The README serves as the user-facing documentation. It contains:

- Project title and description.
- Problem statement.
- Objectives.
- Feature table.
- Technologies used table.
- Project structure.
- Prerequisites (including the Python 3.9 minimum version justification).
- Step-by-step installation instructions for Windows, macOS, and Linux.
- How-to-use instructions for both workflow paths (same session and new session).
- SHA-256 explanation.
- Safety considerations and limitations table.
- Five manual testing scenarios with expected results.
- Seven future enhancement ideas.
- License note.

---

### 10.4 `PROJECT_REPORT.md`

This file. A complete college-style project report covering all aspects of the
application from problem statement through to references. It describes only features
that are implemented in the current version of `app.py` and clearly distinguishes
planned test cases from executed ones.

### Built-in Self-Test Suite (inside `app.py`)

`app.py` contains a 70-test self-test suite at the very bottom of the file, inside an
`if __name__ == "__main__":` block. When Streamlit imports the file normally, this
block is skipped. When you run `python app.py` directly, the tests execute and the
Streamlit UI code does not launch a browser.

**Functions tested:**

| Function | Tests |
|---|---|
| `compute_sha256` | Known digest, determinism, empty input, avalanche effect, output length, output charset, 1 MB chunked input, cross-check against `hashlib` directly |
| `format_file_size` | Eight boundary cases from 0 B through 10 MB |
| `is_valid_sha256` | Five valid cases, eight invalid cases including `None`, wrong length, uppercase, non-hex, and embedded space |
| `validate_record` | Well-formed record accepted; each of the five required fields tested for absence individually; wrong tool name; six invalid SHA-256 formats |
| `build_record` | All five fields preserved; output passes `validate_record`; JSON serialisation round-trip |
| `build_verification_report` | UNCHANGED and MODIFIED reports checked for required content and safety note |

**How to run:**

```bash
python app.py
```

Streamlit prints harmless "bare mode" warnings to stderr — these can be ignored.
The test results appear in stdout.

**Confirmed result** (executed during code review):

```
============================================================
  70 passed  /  0 failed  /  70 total
============================================================
```

---

## 11. Main Features

### 11.1 SHA-256 Hash Computation

Any file up to 10 MB in size can be uploaded. The application reads the file's raw bytes
into memory and processes them through `hashlib.sha256()` in 64 KB chunks. The resulting
64-character hexadecimal digest is displayed in a styled, selectable text area. This
feature works without recording any reference; the user can simply upload a file to see
its hash.

### 11.2 Original Reference Recording

After a hash is computed, the user can click "Record as original reference". This saves
the hash, the filename, and the current UTC timestamp to `st.session_state`. These values
persist across widget interactions within the session but are cleared when the browser tab
is refreshed or closed.

### 11.3 JSON Verification Record Export

The user can expand the "Active reference hash" panel and download the recorded reference
as a `.json` file. The file has the following structure:

```json
{
  "schema_version": "1",
  "tool": "FileGuard",
  "original_filename": "contract.pdf",
  "sha256": "e3b0c44298fc1c149afb4c8996fb924...",
  "recorded_at_utc": "2025-01-15T10:23:00Z"
}
```

The filename follows the pattern `fileguard_<original_filename>.json`. The record can be
stored on any medium and imported in a future session.

### 11.4 JSON Verification Record Import and Validation

In Step 2 Option A, the user can upload a previously exported `.json` record. The
application:

1. Parses it with `json.loads()` — it is never executed.
2. Checks that all five required fields are present.
3. Checks that the `"tool"` field equals `"FileGuard"`.
4. Checks that the `"sha256"` field matches `[0-9a-f]{64}` exactly.

If any check fails, a specific error message is shown. If all checks pass, the imported
hash and metadata are displayed and used as the reference for comparison.

### 11.5 File Verification and Verdict

Once a reference hash is available (either from the session state or an imported record),
the user uploads the file to verify in Option B. The application computes the file's
current hash and compares it to the reference using a direct string equality check.

- **If they match:** a teal banner with title "✅ File Unchanged" and a sub-line
  confirming byte-for-byte identity is shown.
- **If they differ:** a red banner with title "⚠️ File Modified" and a sub-line directing
  the user to the hash diff below is shown.

### 11.6 Side-by-Side Hash Comparison and Character-Level Diff

When hashes match, the original reference hash and the current file's hash are shown in
two adjacent `st.text_area` widgets in teal monospace text — both identical, confirming
the match.

When hashes differ, the original is shown in a text area while the current hash is
rendered by `render_hash_diff()` as an HTML character-level diff: positions that match
the original are coloured teal, and positions that differ are coloured red with a dark
red background highlight. This lets the user see exactly where in the 64-character digest
the values diverge.

### 11.7 Verification Report Download

After a comparison, a "Download verification report (.txt)" button appears. The report
is a plain-text file with the following structure:

```
==============================================================
  FileGuard — Verification Report
==============================================================

Verified at (UTC)    : 2025-01-15T11:05:32Z
Result               : UNCHANGED

--- Reference (original) ---
Filename             : contract.pdf
Source               : Step 1 session recording (recorded 2025-01-15T10:23:00Z)
SHA-256              : e3b0c44298fc1c149afb4c8996fb924...

--- File checked ---
Filename             : contract.pdf
SHA-256              : e3b0c44298fc1c149afb4c8996fb924...

==============================================================
Hashes match         : YES — file is unchanged
...
```

The report filename encodes the checked filename and the verification timestamp.

### 11.8 Live Sidebar Dashboard

The sidebar is always visible (on wide-layout screens) and shows:

- A three-step workflow overview.
- A "Current session status" panel that displays either a green "Reference recorded" pill
  (with the filename, UTC timestamp, and full hash) or a grey "No reference recorded yet"
  pill.

The sidebar updates automatically whenever the recorded hash changes.

### 11.9 Safety Explanations

After every verification result, the application shows:

- A plain-language explanation of what the result means and what it does not mean.
- On a mismatch: a bulleted list of possible explanations, explicitly stating that a
  mismatch does not automatically mean malicious tampering.
- On a match: a note that byte-for-byte identity does not prove the file is free of
  malware.
- A yellow trust-reminder panel explaining that the reference record is only reliable if
  it has itself been protected from modification.

### 11.10 Visual Step-Progress Tracker

A pill-row directly beneath the main header shows three stages:
**Step 1 — Record hash › Step 2 — Verify file › Export report**.
Before any reference is recorded, Step 1 is the active pill. Once a reference is
recorded, Step 1 turns green with a ✅ tick and Step 2 becomes active. This gives users
an immediate sense of where they are in the workflow without scrolling.

### 11.11 Two-Column Verify Layout

Step 2 renders Option A (load a saved JSON record) and Option B (upload the file to
check) side-by-side in `st.columns(2, gap="large")`. Each column has a styled badge
header. This makes it visually clear that the two options are parallel inputs that feed
the same comparison, not sequential steps.

---

## 12. Testing Plan

> **Important note on test status:**
> Section 12.1 contains the **automated unit tests** executed during the code review for
> this project. Section 12.2 contains **planned manual tests** that describe how each
> UI feature can be verified by running the application. Manual tests have not been
> executed in a formal, documented test environment; their "Expected Result" column
> describes the behaviour defined by the code.

### 12.1 Test Cases

| TC # | Category | Input | Steps | Expected Result |
|---|---|---|---|---|
| TC-01 | Hash computation | A plain text file containing `Hello, World!\n` | Upload in Step 1 | A 64-character hex digest is displayed in the hash text area; the success banner appears |
| TC-02 | Determinism | The same file uploaded twice in the same session | Upload once, note the hash; upload again | Both hash displays show the identical 64-character string |
| TC-03 | Avalanche effect | A text file; then the same file with one character changed | Upload original, note hash; upload modified file in Step 2 | The two hashes are completely different; the verdict banner is red |
| TC-04 | File unchanged | Any file | Record hash in Step 1; upload the exact same file in Step 2 | Green "✅ File Unchanged" verdict banner; both hash text areas show the same value |
| TC-05 | File modified | Any text file | Record hash in Step 1; edit one character and save; upload modified file in Step 2 | Red "⚠️ File Modified" verdict banner; hash text areas show different values |
| TC-06 | Oversized file | Any file larger than 10 MB | Upload in Step 1 | Red error message stating the file is too large; no hash is computed |
| TC-07 | Empty file | A 0-byte file | Upload in Step 1 | Yellow warning message stating the file is empty; no hash is computed |
| TC-08 | JSON export | Any file with a recorded hash | Expand "Active reference hash" panel; click "Download verification record (.json)" | A `.json` file is downloaded; opening it in a text editor shows all five required fields |
| TC-09 | JSON import — valid record | The `.json` file downloaded in TC-08 | Upload in Step 2 Option A | Green success message; the original filename and timestamp are displayed; the reference hash appears in a text area |
| TC-10 | JSON import — missing fields | A `.json` file containing `{ "hello": "world" }` | Upload in Step 2 Option A | Red error message listing the missing required fields |
| TC-11 | JSON import — wrong tool | A `.json` file with all required fields but `"tool": "OtherApp"` | Upload in Step 2 Option A | Red error message: "Record was not created by FileGuard." |
| TC-12 | JSON import — invalid hash format | A valid-structure record with `"sha256": "not-a-hash"` | Upload in Step 2 Option A | Red error message stating the sha256 field is not a valid 64-character hex digest |
| TC-13 | JSON import — not valid JSON | A plain text file renamed to `.json` | Upload in Step 2 Option A | Red error message stating the file could not be parsed as JSON |
| TC-14 | Verify without reference | Upload a file in Step 2 Option B with no session reference and no JSON record uploaded | Upload any file | Yellow warning message stating no reference hash is available |
| TC-15 | Cross-session verification | Record and export a hash in one session; refresh the browser; import the JSON; upload the original file | Steps as described | Verification succeeds using the imported record; result matches TC-04 expectation |
| TC-16 | Verification report — match | Complete a successful verification (TC-04) | Click "Download verification report (.txt)" | A `.txt` file is downloaded; it contains both hashes, the UTC timestamp, and the result "UNCHANGED" |
| TC-17 | Verification report — mismatch | Complete a failed verification (TC-05) | Click "Download verification report (.txt)" | A `.txt` file is downloaded; it contains both hashes, the UTC timestamp, and the result "MODIFIED" |
| TC-18 | Clear recorded hash | Record a hash; expand the reference panel; click "🗑️ Clear" | Steps as described | The sidebar switches to the "No reference recorded yet" pill; the reference panel disappears |
| TC-19 | Sidebar status update | Record a hash in Step 1 | Observe the sidebar | The sidebar shows the filename, UTC timestamp, and full hash immediately after recording |
| TC-20 | File type independence | An image file (.jpg), a PDF, and an executable (.exe) | Upload each in Step 1 | A valid 64-character hash is displayed for each; no errors related to file type |

### 12.1 Automated Unit Tests — Executed

The built-in self-test suite inside `app.py` was run with `python app.py` during the
code review for this project. The confirmed stdout output is:

```
============================================================
  FileGuard — automated helper-function tests
============================================================

--- compute_sha256 ---     8 tests
--- format_file_size ---   8 tests
--- is_valid_sha256 ---   13 tests
--- validate_record ---   20 tests
--- build_record ---       8 tests
--- build_verification_report ---  9 tests
--- size-limit arithmetic ---      4 tests

============================================================
  70 passed  /  0 failed  /  70 total
============================================================
```

These tests cover: correct SHA-256 computation, determinism, avalanche effect, output
length and charset, chunked reading of 1 MB input, file-size formatting, hash format
validation, JSON record construction and validation (all required fields, tool sentinel,
hash format), JSON serialisation round-trip, and verification report content.

### 12.2 Planned Manual Tests

The test cases below describe how each UI feature can be verified by running
`streamlit run app.py` in a browser. They have not been executed in a formal,
documented test environment. The "Expected Result" column describes behaviour defined
by the code, not an observed outcome.

| TC # | Category | Input | Steps | Expected Result |
|---|---|---|---|---|
| TC-01 | Hash computation | A plain text file | Upload in Step 1 | A 64-character hex digest is displayed; the success banner appears |
| TC-02 | Determinism | The same file uploaded twice | Upload once, note hash; upload again | Both hash displays show the identical 64-character string |
| TC-03 | Avalanche effect | A text file; then the same file with one character changed | Upload original, note hash; upload modified file in Step 2 | The two hashes are completely different; the verdict banner is red |
| TC-04 | File unchanged | Any file | Record hash in Step 1; upload exact same file in Step 2 | Green "✅ File Unchanged" banner; both hash text areas show the same value |
| TC-05 | File modified | Any text file | Record hash in Step 1; edit one character and save; upload in Step 2 | Red "⚠️ File Modified" banner; character-level diff shows differing positions in red |
| TC-06 | Oversized file | Any file larger than 10 MB | Upload in Step 1 | Red error message; no hash is computed |
| TC-07 | Empty file | A 0-byte file | Upload in Step 1 | Yellow warning message; no hash is computed |
| TC-08 | JSON export | Any file with a recorded hash | Expand reference panel; click download | A `.json` file is downloaded containing all five required fields |
| TC-09 | JSON import — valid record | The `.json` file from TC-08 | Upload in Step 2 Option A | Green success message with original filename and timestamp |
| TC-10 | JSON import — missing fields | `{ "hello": "world" }` renamed `.json` | Upload in Step 2 Option A | Red error listing the missing required fields |
| TC-11 | JSON import — wrong tool | Valid structure but `"tool": "OtherApp"` | Upload in Step 2 Option A | Red error: "Record was not created by FileGuard." |
| TC-12 | JSON import — invalid hash | Valid structure but `"sha256": "not-a-hash"` | Upload in Step 2 Option A | Red error: sha256 field is not a valid hex digest |
| TC-13 | JSON import — not valid JSON | A plain text file renamed `.json` | Upload in Step 2 Option A | Red error: file could not be parsed as JSON |
| TC-14 | Verify without reference | Upload in Option B with no session reference and no JSON | Upload any file | Yellow warning: no reference hash available |
| TC-15 | Cross-session verification | Record and export hash; refresh browser; import JSON; upload file | Steps as described | Verification succeeds using the imported record |
| TC-16 | Report download — match | Complete TC-04 | Click download report button | `.txt` file contains both hashes, UTC timestamp, and result "UNCHANGED" |
| TC-17 | Report download — mismatch | Complete TC-05 | Click download report button | `.txt` file contains both hashes, UTC timestamp, and result "MODIFIED" |
| TC-18 | Clear recorded hash | Record a hash; click "🗑️ Clear" in reference panel | Steps as described | Sidebar switches to "No reference yet" pill |
| TC-19 | Step tracker updates | Record a hash in Step 1 | Observe the tracker row | Step 1 pill turns green with ✅; Step 2 pill becomes active |
| TC-20 | File type independence | An image, a PDF, and an executable | Upload each in Step 1 | A valid 64-character hash is displayed for each |

### 12.3 Notes on Testing

- TC-06 requires a file larger than 10 MB. Any large video or archive file can be used.
- TC-07 can be created on Windows with `New-Item empty.txt -ItemType File` or on
  Linux/macOS with `touch empty.txt`.
- The built-in self-tests run any time with `python app.py`. Streamlit's "bare mode"
  warnings on stderr are harmless and can be ignored.

---

## 13. Results and Discussion

### 13.1 Features Implemented

All nine objectives stated in Section 3 have been implemented in the current version of
`app.py`. The table below maps each objective to the corresponding implementation:

| Objective | Implemented as |
|---|---|
| Compute SHA-256 hash locally | `compute_sha256()` using `hashlib.sha256()` with 64 KB chunked reads |
| Record original reference | "Record as original reference" button writing to `st.session_state` |
| Export as JSON | `build_record()` + `st.download_button` in the reference expander |
| Import and validate JSON | `json.loads()` + `validate_record()` in Step 2 Option A |
| Compare and display verdict | String equality check + colour-coded verdict banner |
| Side-by-side hash display | Two `st.text_area` widgets in `st.columns(2)` |
| Downloadable report | `build_verification_report()` + `st.download_button` |
| Plain-language explanation | `info-panel` divs shown conditionally after each verdict |
| Safety controls | Size limit, empty check, no-exec policy, schema validation, honest messaging |

### 13.2 Observed Design Outcomes

The following are design decisions and their expected effects, based on code inspection
rather than user testing:

- **Selectable text areas for hashes** replace static HTML divs, making it easy for users
  to select and copy a hash without needing to triple-click or use browser developer tools.
- **Two-column hash comparison** places the original and current hash directly beside each
  other, reducing the effort needed to spot that they are identical or different.
- **Character-level hash diff** (`render_hash_diff()`) highlights the exact positions in
  the current hash that differ from the original, making it easy to see how many
  characters changed and where — rather than just knowing the hashes are different.
- **Visual step-progress tracker** beneath the header updates live: Step 1 turns green
  once a reference is recorded, and Step 2 becomes the active step.
- **Live sidebar dashboard** means the user does not need to scroll back to Step 1 to
  confirm which reference is currently active.
- **Status pills** in both the sidebar and the Step 2 section provide consistent,
  immediate feedback about session state.

### 13.3 Limitations Observed During Development

These are structural limitations identified by inspecting the code and architecture, not
the results of testing:

- Session state is lost on browser refresh. A user who forgets to export the JSON record
  before closing the tab must re-upload the original file.
- Only one reference hash can be active per session at a time. Verifying multiple files
  against different references requires clearing and re-recording between each.
- The 10 MB file size limit is enforced in Python. Streamlit's own server configuration
  may impose a separate limit; if the Streamlit default is lower than 10 MB, the Python
  check may never be reached.
- The application depends on the user's browser tab remaining open during the session.
  There is no background process or persistent storage.

---

## 14. Advantages

1. **No installation complexity for the end user.** Once Python and Streamlit are
   installed, the application starts with a single command.

2. **No external dependencies beyond Streamlit.** All cryptographic and data handling
   logic uses Python's standard library, which is audited, maintained, and version-stable.

3. **Completely local.** No data ever leaves the user's machine. This makes the tool
   suitable for verifying sensitive documents — legal contracts, medical records,
   configuration files — without privacy concerns.

4. **Files are never executed.** The application reads only raw bytes. It cannot be
   tricked into running a malicious file that is uploaded to it.

5. **Cross-session verification.** The JSON export/import mechanism allows a hash
   recorded today to be used to verify the same file weeks later, without requiring the
   original session to still be open.

6. **Honest about limitations.** The application does not overstate what SHA-256
   verification proves. It explicitly tells the user that a match confirms identity only,
   not safety, and that a mismatch has multiple possible explanations.

7. **Educational value.** The SHA-256 explainer, the side-by-side hash comparison, and
   the plain-language result explanations teach the user about cryptographic hashing
   through direct interaction rather than passive reading.

8. **Accessible to beginners.** The entire workflow is presented as two numbered steps.
   No command-line knowledge, no manual hash copying, and no technical background is
   required.

---

## 15. Limitations

1. **Single file per session.** Only one reference hash can be recorded per browser
   session. Batch verification of multiple files is not supported.

2. **Session volatility.** The recorded reference hash is stored in Streamlit session
   state, which is lost when the browser tab is refreshed or closed. If the user does not
   export the JSON record, the reference is permanently lost.

3. **No `pytest` integration or CI pipeline.** The built-in self-test suite (inside `app.py`
   under `if __name__ == "__main__":`) covers all pure helper functions but must be run
   manually. There is no automated test runner configured to run on every code change.

4. **10 MB file size limit.** Large files — ISO images, video files, database dumps —
   cannot be verified. This is a deliberate constraint to avoid excessive memory usage
   in a single-process Streamlit application, but it limits the tool's applicability to
   large-file scenarios.

5. **SHA-256 only.** The application does not support other hash algorithms (MD5, SHA-1,
   SHA-512). While MD5 and SHA-1 are cryptographically weakened, they are still widely
   used in legacy systems for interoperability.

6. **No digital signature on the JSON record.** The JSON verification record can be
   tampered with after it is exported. If an attacker can modify both the file and the
   record, the comparison provides no integrity guarantee. The application warns about
   this but cannot prevent it.

7. **No verification history.** Each comparison session starts fresh. There is no log or
   audit trail within the application itself, beyond the single downloadable report.

8. **Browser dependency.** The application requires a browser tab to remain open for the
   duration of a session. It cannot run as a background service or be called from a script.

---

## 16. Future Enhancements

The following features are not currently implemented. They are listed in approximate order
of implementation priority.

| Priority | Enhancement | Description |
|---|---|---|
| 1 | Verification history log | A table showing all files verified in the current session, with their hashes and results |
| 2 | Multiple file comparison | Accept a batch of files and verify each against a corresponding reference in a single pass |
| 3 | PDF report export | Generate a formatted PDF version of the verification report using a library such as `reportlab` or `fpdf2` |
| 4 | Hash algorithm selection | Allow the user to choose SHA-256, SHA-512, or SHA-1 (with a clear warning about SHA-1's weaknesses) |
| 5 | Digital signature on the JSON record | Sign the record with a private key using the `cryptography` library, so that any modification to the record can be detected independently |
| 6 | pytest integration | Migrate the built-in self-test suite to `pytest` with a CI configuration so tests run automatically on every code change |
| 7 | Command-line companion | A `cli.py` script that exposes the same record/verify workflow via `argparse` for scripted or automated use |
| 8 | Drag-and-drop record detection | Automatically detect whether a dropped file in Step 2 is a FileGuard JSON record or a file to be verified, removing the need for separate uploaders |

---

## 17. Conclusion

FileGuard demonstrates a practical application of cryptographic hashing to the real-world
problem of file integrity verification. By wrapping Python's `hashlib.sha256()` in a
Streamlit interface, the project makes a professional-grade security technique accessible
to users with no terminal or cryptography background.

The application covers the complete verification workflow: hash a file, record the
reference, export it for safe keeping, reload it in a future session, compare the current
hash of the file, interpret the result, and download a report. Each step is designed to be
self-explanatory, with inline instructions and honest explanations of what the results
mean and where the limits of hash-based verification lie.

The codebase is intentionally minimal — four files, one external dependency — making it
straightforward to understand, extend, and audit.
The safety controls embedded in the design reflect sound principles: no file execution, no
data transmission, enforced input limits, structured validation of imported data, and
careful honesty about what the tool can and cannot guarantee.

This project demonstrates competence in Python programming, web application development
with Streamlit, cryptographic concepts, input validation, session management, structured
data exchange with JSON, and security-aware software design.

---

## 18. References

1. National Institute of Standards and Technology —
   *FIPS PUB 180-4: Secure Hash Standard (SHS)*, August 2015.
   https://csrc.nist.gov/publications/detail/fips/180/4/final

2. Python Software Foundation — `hashlib` — Secure hashes and message digests.
   Python 3 Standard Library Documentation.
   https://docs.python.org/3/library/hashlib.html

3. Python Software Foundation — `io` — Core tools for working with streams.
   Python 3 Standard Library Documentation.
   https://docs.python.org/3/library/io.html

4. Python Software Foundation — `json` — JSON encoder and decoder.
   Python 3 Standard Library Documentation.
   https://docs.python.org/3/library/json.html

5. Python Software Foundation — `re` — Regular expression operations.
   Python 3 Standard Library Documentation.
   https://docs.python.org/3/library/re.html

6. Python Software Foundation — `datetime` — Basic date and time types.
   Python 3 Standard Library Documentation.
   https://docs.python.org/3/library/datetime.html

7. Streamlit Inc. — Streamlit API Reference.
   https://docs.streamlit.io/develop/api-reference

8. Streamlit Inc. — Session State documentation.
   https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state

9. PCI Security Standards Council — *PCI DSS v4.0*, Requirement 11.5:
   Unauthorised changes on payment card systems are detected and addressed.
   March 2022. https://www.pcisecuritystandards.org

10. Center for Internet Security — *CIS Controls v8*, Control 3:
    Data Protection — Know your data; protect it wherever it goes.
    https://www.cisecurity.org/controls/v8

---

*End of Report — FileGuard v4.0*
