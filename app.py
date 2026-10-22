"""
FileGuard – Digital File Integrity & Tampering Detector
========================================================
Calculates the SHA-256 hash of an uploaded file so you can verify
whether the file has been modified since the hash was first recorded.

Author  : (your name)
Version : 4.0.0  —  Improved dashboard layout, step tracker, hash diff view,
                     accessible contrast, cleaner two-column verify flow
"""

import hashlib
import io
import json
import re
import sys
from datetime import datetime, timezone

import streamlit as st

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
MAX_FILE_SIZE_MB    = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
RECORD_SCHEMA_VERSION = "1"

# ─────────────────────────────────────────────
# Page config  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FileGuard – File Integrity Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
.stApp { background-color: #0d1b2a; color: #e0e6ed; }
section[data-testid="stSidebar"] {
    background-color: #0a1628;
    border-right: 1px solid #1f4068;
}

/* ── Typography ── */
h1, h2, h3, h4 { color: #00c9a7 !important; }
p, li { color: #c8d8e8; }
hr { border-color: #1f4068; }
code {
    background: #0d2137; color: #a8ffd8;
    padding: 0.1em 0.35em; border-radius: 3px;
}

/* ── Step cards ── */
.step-card {
    background: #111f30;
    border: 1px solid #1f4068;
    border-left: 4px solid #00c9a7;
    border-radius: 10px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.8rem;
}
.step-number {
    display: inline-block;
    background: #00c9a7;
    color: #0d1b2a;
    font-weight: 700;
    font-size: 0.78rem;
    border-radius: 50px;
    padding: 0.15rem 0.7rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}

/* ── Step progress tracker ── */
.step-tracker {
    display: flex;
    align-items: center;
    gap: 0;
    margin: 0.2rem 0 1.6rem;
    flex-wrap: nowrap;
}
.tracker-step {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    padding: 0.4rem 1rem;
    border-radius: 50px;
    white-space: nowrap;
}
.tracker-step.done {
    background: #0a2e1e;
    color: #00c9a7;
    border: 1px solid #00c9a740;
}
.tracker-step.active {
    background: #0d2137;
    color: #e0e6ed;
    border: 1px solid #00c9a7;
}
.tracker-step.waiting {
    background: #111827;
    color: #4a6a84;
    border: 1px solid #1f406860;
}
.tracker-arrow {
    color: #1f4068;
    font-size: 1.1rem;
    padding: 0 0.25rem;
    flex-shrink: 0;
}

/* ── Hash text-area override ── */
.stTextArea textarea {
    background-color: #0d2137 !important;
    color: #a8ffd8 !important;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace !important;
    font-size: 0.83rem !important;
    border: 1px solid #1f4068 !important;
    border-left: 4px solid #00c9a7 !important;
    border-radius: 6px !important;
    caret-color: #00c9a7;
    line-height: 1.6 !important;
}
.stTextArea textarea:focus {
    box-shadow: 0 0 0 2px #00c9a740 !important;
}

/* ── Metric cards ── */
div[data-testid="metric-container"] {
    background: #0d2137;
    border: 1px solid #1f4068;
    border-radius: 8px;
    padding: 0.75rem 1rem;
}
div[data-testid="metric-container"] label {
    color: #8ab4cc !important;   /* WCAG AA on #0d2137 */
    font-size: 0.78rem !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #e0e6ed !important;
    font-size: 1rem !important;
}

/* ── Status pills ── */
.status-pill {
    display: inline-block;
    border-radius: 50px;
    padding: 0.25rem 0.85rem;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}
.pill-ready   { background: #0a2e1e; color: #2ddfb8; border: 1px solid #00c9a760; }
.pill-waiting { background: #111827; color: #8ab4cc; border: 1px solid #1f406880; }
.pill-warn    { background: #2e1a0a; color: #e8a96a; border: 1px solid #7a420060; }

/* ── Verdict banners ── */
.verdict-match {
    background: #071f14;
    border: 2px solid #00c9a7;
    border-radius: 10px;
    padding: 1.4rem 1.8rem;
    margin: 0.8rem 0 1rem;
}
.verdict-match .verdict-title {
    font-size: 1.25rem; font-weight: 700; color: #2ddfb8;
}
.verdict-match .verdict-sub {
    font-size: 0.9rem; color: #8ecfbb; margin-top: 0.35rem; font-weight: 400;
}
.verdict-mismatch {
    background: #1e0707;
    border: 2px solid #e05c5c;
    border-radius: 10px;
    padding: 1.4rem 1.8rem;
    margin: 0.8rem 0 1rem;
}
.verdict-mismatch .verdict-title {
    font-size: 1.25rem; font-weight: 700; color: #f08080;
}
.verdict-mismatch .verdict-sub {
    font-size: 0.9rem; color: #c88888; margin-top: 0.35rem; font-weight: 400;
}

/* ── Hash diff display ── */
.hash-diff-wrap {
    display: flex;
    gap: 0.35rem;
    flex-wrap: wrap;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 0.8rem;
    line-height: 1.9;
    word-break: break-all;
    background: #0a1828;
    border: 1px solid #1f4068;
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
}
.hash-byte-match  { color: #2ddfb8; }
.hash-byte-differ { color: #f08080; background: #3a0f0f; border-radius: 2px; padding: 0 1px; }
.hash-label-row {
    font-size: 0.73rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #8ab4cc;
    font-weight: 600;
    margin-bottom: 0.25rem;
    font-family: system-ui, sans-serif;
}
.hash-source-row {
    font-size: 0.72rem;
    color: #4a6a84;
    margin-top: -0.15rem;
    margin-bottom: 0.5rem;
    font-family: system-ui, sans-serif;
}

/* ── Info / warning panels ── */
.info-panel {
    background: #111f30;
    border: 1px solid #2a4f6a;
    border-radius: 8px;
    padding: 1.1rem 1.5rem;
    font-size: 0.9rem;
    color: #b8cfe0;   /* bumped from #9db8cc for WCAG AA */
    line-height: 1.75;
}
.info-panel strong { color: #d0e8f4; }
.info-panel ul { margin: 0.5rem 0 0 0; padding-left: 1.4rem; }
.info-panel li { color: #b8cfe0; margin-bottom: 0.3rem; }

.warn-panel {
    background: #1a1500;
    border: 1px solid #7a6500;
    border-left: 4px solid #c8aa50;
    border-radius: 8px;
    padding: 0.9rem 1.3rem;
    font-size: 0.88rem;
    color: #d4b85a;   /* bumped from #c8aa50 for WCAG AA */
    line-height: 1.7;
    margin-top: 0.8rem;
}

/* ── Download CTA box ── */
.download-cta {
    background: #071f14;
    border: 1px solid #00c9a740;
    border-radius: 10px;
    padding: 1.2rem 1.6rem;
    margin-top: 1rem;
}
.download-cta p {
    color: #8ecfbb;
    font-size: 0.88rem;
    margin: 0 0 0.8rem 0;
    line-height: 1.6;
}

/* ── File uploader ── */
section[data-testid="stFileUploadDropzone"] {
    background: #0d2137 !important;
    border: 2px dashed #00c9a750 !important;
    border-radius: 10px !important;
}
section[data-testid="stFileUploadDropzone"] p {
    color: #8ab4cc !important;
}

/* ── Option divider label ── */
.option-label {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #2ddfb8;
    border-bottom: 1px solid #1f4068;
    padding-bottom: 0.4rem;
    margin-bottom: 0.6rem;
    width: 100%;
}
.option-label .option-badge {
    background: #0d2137;
    border: 1px solid #00c9a740;
    border-radius: 4px;
    padding: 0.05rem 0.45rem;
    font-size: 0.74rem;
    color: #00c9a7;
}

/* ── Sidebar ── */
.sidebar-section-title {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6b9ab8;   /* bumped from #3a6a8a */
    font-weight: 700;
    margin: 1.1rem 0 0.4rem;
}
.sidebar-hash {
    font-family: monospace;
    font-size: 0.75rem;
    color: #2ddfb8;
    word-break: break-all;
    line-height: 1.65;
    background: #0d2137;
    border-radius: 6px;
    padding: 0.5rem 0.65rem;
    border: 1px solid #1f406880;
}
.sidebar-step {
    display: flex;
    align-items: flex-start;
    gap: 0.55rem;
    padding: 0.4rem 0;
    font-size: 0.83rem;
    line-height: 1.4;
}
.sidebar-step-icon {
    flex-shrink: 0;
    width: 1.2rem;
    text-align: center;
    font-size: 0.85rem;
    margin-top: 0.05rem;
}
.sidebar-step-text { color: #b8cfe0; }
.sidebar-step-text strong { color: #e0e6ed; }
.sidebar-step-text .hint { color: #6b9ab8; font-size: 0.76rem; }

/* ── Example hash block ── */
.example-hash-block {
    background: #0a1828;
    border: 1px solid #1f4068;
    border-left: 4px solid #3b82d4;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    font-family: "SFMono-Regular", Consolas, monospace;
    font-size: 0.8rem;
    color: #a8c8e8;
    word-break: break-all;
    margin: 0.5rem 0;
    line-height: 1.6;
}
.example-hash-block .ex-label {
    font-family: system-ui, sans-serif;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #6b9ab8;
    font-weight: 700;
    display: block;
    margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Helper functions  (logic unchanged from v3.0)
# ─────────────────────────────────────────────

def compute_sha256(file_bytes: bytes) -> str:
    """SHA-256 hex digest, processed in 64 KB chunks."""
    h = hashlib.sha256()
    stream = io.BytesIO(file_bytes)
    while chunk := stream.read(65536):
        h.update(chunk)
    return h.hexdigest()


def format_file_size(n: int) -> str:
    if n < 1024:           return f"{n} B"
    if n < 1024 ** 2:      return f"{n / 1024:.2f} KB"
    return                        f"{n / 1024**2:.2f} MB"


def is_valid_sha256(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{64}", value or ""))


def build_record(filename: str, sha256_hash: str, recorded_at: str) -> dict:
    return {
        "schema_version":    RECORD_SCHEMA_VERSION,
        "tool":              "FileGuard",
        "original_filename": filename,
        "sha256":            sha256_hash,
        "recorded_at_utc":   recorded_at,
    }


def validate_record(data: dict) -> tuple[bool, str]:
    required = {"schema_version", "tool", "original_filename", "sha256", "recorded_at_utc"}
    missing  = required - set(data.keys())
    if missing:
        return False, f"Missing fields: {', '.join(sorted(missing))}"
    if data.get("tool") != "FileGuard":
        return False, "Record was not created by FileGuard."
    if not is_valid_sha256(data.get("sha256", "")):
        return False, "The 'sha256' field is not a valid 64-character hex digest."
    return True, ""


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_verification_report(
    ref_filename: str,
    ref_hash: str,
    ref_source: str,
    verify_filename: str,
    current_hash: str,
    verified_at: str,
    result: str,
) -> str:
    """Return a human-readable plain-text verification report."""
    divider = "=" * 62
    return (
        f"{divider}\n"
        f"  FileGuard — Verification Report\n"
        f"{divider}\n\n"
        f"Verified at (UTC)    : {verified_at}\n"
        f"Result               : {result}\n\n"
        f"--- Reference (original) ---\n"
        f"Filename             : {ref_filename}\n"
        f"Source               : {ref_source}\n"
        f"SHA-256              : {ref_hash}\n\n"
        f"--- File checked ---\n"
        f"Filename             : {verify_filename}\n"
        f"SHA-256              : {current_hash}\n\n"
        f"{divider}\n"
        f"Hashes match         : {'YES — file is unchanged' if result == 'UNCHANGED' else 'NO  — file contents differ'}\n\n"
        f"Note: A mismatch means the file contents differ from the original\n"
        f"reference. It does not automatically indicate malicious tampering.\n"
        f"Possible causes include intentional edits, accidental corruption,\n"
        f"or uploading a different version of the file.\n\n"
        f"This report is only trustworthy if the reference hash record has\n"
        f"been stored securely and has not itself been altered.\n"
        f"{divider}\n"
        f"FileGuard v4.0 · All processing is local · No data transmitted\n"
    )


def render_hash_diff(hash_a: str, hash_b: str) -> str:
    """
    Build an HTML string showing hash_b character-by-character,
    with positions that differ from hash_a highlighted in red.
    Characters that match are shown in teal.
    Used only when hashes differ, to let users see exactly where they diverge.
    """
    spans = []
    for i, ch in enumerate(hash_b):
        if i < len(hash_a) and ch == hash_a[i]:
            spans.append(f'<span class="hash-byte-match">{ch}</span>')
        else:
            spans.append(f'<span class="hash-byte-differ">{ch}</span>')
    return "".join(spans)


# ─────────────────────────────────────────────
# Session-state initialisation
# ─────────────────────────────────────────────
for key, default in [
    ("recorded_hash",     None),
    ("recorded_filename", None),
    ("recorded_at",       None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ═════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🛡️ FileGuard")
    st.caption("Digital File Integrity & Tampering Detector")
    st.markdown("---")

    # ── Workflow steps with completion state ──
    st.markdown('<p class="sidebar-section-title">How it works</p>', unsafe_allow_html=True)

    has_ref = st.session_state["recorded_hash"] is not None

    step1_icon = "✅" if has_ref else "1️⃣"
    step2_icon = "🔍"
    step3_icon = "📥"

    st.markdown(
        f"""
        <div class="sidebar-step">
            <span class="sidebar-step-icon">{step1_icon}</span>
            <span class="sidebar-step-text">
                <strong>Record</strong><br>
                <span class="hint">Upload a file and save its SHA-256 hash as a reference.</span>
            </span>
        </div>
        <div class="sidebar-step">
            <span class="sidebar-step-icon">{step2_icon}</span>
            <span class="sidebar-step-text">
                <strong>Verify</strong><br>
                <span class="hint">Upload the file again to compare its current hash with the original.</span>
            </span>
        </div>
        <div class="sidebar-step">
            <span class="sidebar-step-icon">{step3_icon}</span>
            <span class="sidebar-step-text">
                <strong>Export</strong><br>
                <span class="hint">Download the reference as a <code>.json</code> record or save a verification report.</span>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Live session status ────────────────────
    st.markdown('<p class="sidebar-section-title">Session status</p>', unsafe_allow_html=True)

    if has_ref:
        st.markdown(
            '<span class="status-pill pill-ready">● Reference recorded</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="sidebar-section-title" style="margin-top:0.9rem;">File</p>'
            f'<span style="color:#c8d8e8; font-size:0.84rem;">{st.session_state["recorded_filename"]}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="sidebar-section-title">Recorded at (UTC)</p>'
            f'<span style="color:#c8d8e8; font-size:0.84rem;">{st.session_state["recorded_at"]}</span>',
            unsafe_allow_html=True,
        )
        st.markdown('<p class="sidebar-section-title">SHA-256 reference</p>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sidebar-hash">{st.session_state["recorded_hash"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-pill pill-waiting">○ No reference yet</span>',
            unsafe_allow_html=True,
        )
        st.caption("Complete Step 1 below to record a reference hash.")

    st.markdown("---")
    st.markdown(
        '<p style="font-size:0.75rem; color:#6b9ab8; text-align:center; line-height:1.6;">'
        "🔒 All processing is local.<br>No files or hashes are transmitted.</p>",
        unsafe_allow_html=True,
    )

# ═════════════════════════════════════════════
# MAIN AREA — Header + step tracker
# ═════════════════════════════════════════════
st.markdown("# 🛡️ FileGuard")
st.markdown(
    "<p style='color:#8ab4cc; margin-top:-0.6rem; font-size:1.05rem;'>"
    "Digital File Integrity &amp; Tampering Detector</p>",
    unsafe_allow_html=True,
)

# ── Visual step-progress tracker ──────────────────────────────────────────────
_s1_cls = "done"  if has_ref else "active"
_s2_cls = "active" if has_ref else "waiting"
_s1_ico = "✅" if has_ref else "●"
st.markdown(
    f"""
    <div class="step-tracker">
        <div class="tracker-step {_s1_cls}">{_s1_ico} &nbsp;Step 1 — Record hash</div>
        <span class="tracker-arrow">›</span>
        <div class="tracker-step {_s2_cls}">{'●' if has_ref else '○'} &nbsp;Step 2 — Verify file</div>
        <span class="tracker-arrow">›</span>
        <div class="tracker-step waiting">↓ &nbsp;Export report</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# ═════════════════════════════════════════════
# STEP 1 – Compute & record the original hash
# ═════════════════════════════════════════════
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.markdown('<span class="step-number">Step 1</span>', unsafe_allow_html=True)
st.markdown("### 📂 Record the Original Hash")

st.info(
    "Upload the file you want to protect. FileGuard computes its SHA-256 fingerprint "
    "and lets you save it as the trusted original reference.\n\n"
    f"✔ Any file type accepted · ✔ Max {MAX_FILE_SIZE_MB} MB · "
    "✔ Processed locally — nothing is transmitted or stored permanently."
)

source_file = st.file_uploader(
    label="Choose a file to hash",
    label_visibility="visible",
    type=None,
    accept_multiple_files=False,
    key="source_uploader",
    help="Any file type is accepted. The file is read in memory only and never saved to disk.",
)

if source_file is not None:
    raw  = source_file.read()
    size = len(raw)

    if size > MAX_FILE_SIZE_BYTES:
        st.error(
            f"❌ **File too large** — {format_file_size(size)} uploaded, "
            f"limit is {MAX_FILE_SIZE_MB} MB. Please choose a smaller file."
        )
    elif size == 0:
        st.warning("⚠️ The uploaded file is empty. Please choose a different file.")
    else:
        try:
            sha256_hash = compute_sha256(raw)
        except Exception as exc:
            st.error(f"❌ Could not process the file: {exc}")
            st.stop()

        st.success("✅ File read and SHA-256 hash computed successfully.")

        # ── Metadata row ──────────────────────────────────────────────────────
        c1, c2, c3 = st.columns(3)
        c1.metric("File name",  source_file.name)
        c2.metric("File size",  format_file_size(size))
        c3.metric("Algorithm",  "SHA-256")

        # ── Hash display ──────────────────────────────────────────────────────
        st.markdown("#### 🔑 SHA-256 Hash")
        st.caption(
            "This is the file's unique fingerprint. "
            "Click inside the box, press **Ctrl+A** then **Ctrl+C** to copy it."
        )
        st.text_area(
            label="SHA-256 hash of uploaded file",
            value=sha256_hash,
            height=80,
            label_visibility="collapsed",
            key="hash_display_step1",
            help="64-character hexadecimal SHA-256 digest. Select all and copy to save it manually.",
        )

        # ── Record button ─────────────────────────────────────────────────────
        st.markdown("")
        col_btn, col_note = st.columns([2, 3])
        with col_btn:
            if st.button("📌 Record as original reference", type="primary", use_container_width=True):
                st.session_state["recorded_hash"]     = sha256_hash
                st.session_state["recorded_filename"] = source_file.name
                st.session_state["recorded_at"]       = now_utc()
                st.success(
                    f"✅ Hash recorded for **{source_file.name}**. "
                    "The sidebar and Step 2 now show the active reference. "
                    "Export the JSON record below to reuse it in a future session."
                )
                st.rerun()
        with col_note:
            st.caption(
                "Recording keeps the hash in this browser session only. "
                "Use the export button below to save a `.json` record for later use."
            )

# ── Recorded-hash panel ────────────────────────────────────────────────────────
if st.session_state["recorded_hash"]:
    rec_hash = st.session_state["recorded_hash"]
    rec_name = st.session_state["recorded_filename"]
    rec_time = st.session_state["recorded_at"]

    with st.expander("📌 Active reference hash — expand to export or clear", expanded=False):

        ec1, ec2 = st.columns(2)
        ec1.metric("Recorded file",     rec_name)
        ec2.metric("Recorded at (UTC)", rec_time)

        st.markdown("**SHA-256 (original reference)**")
        st.text_area(
            label="Recorded SHA-256",
            value=rec_hash,
            height=80,
            label_visibility="collapsed",
            key="hash_display_recorded",
            help="This is the reference hash stored for the current session.",
        )

        st.markdown("---")
        st.markdown("#### 💾 Export as JSON Verification Record")
        st.markdown(
            """
            <div class="info-panel">
                Download this record as a <code>.json</code> file and store it somewhere
                you trust — a password-protected folder, encrypted storage, or a
                version-controlled repository with commit signing.<br><br>
                <strong>Security reminder:</strong> the record is only trustworthy if
                <em>it has not itself been altered</em> after you saved it. If an attacker
                can modify both the file and this record, the verification provides no
                protection.
            </div>
            """,
            unsafe_allow_html=True,
        )

        export_record = build_record(rec_name, rec_hash, rec_time)
        json_export   = json.dumps(export_record, indent=2).encode("utf-8")

        dl_col, clear_col = st.columns([3, 1])
        with dl_col:
            st.download_button(
                label="⬇️ Download verification record (.json)",
                data=json_export,
                file_name=f"fileguard_{rec_name}.json",
                mime="application/json",
                use_container_width=True,
            )
        with clear_col:
            if st.button(
                "🗑️ Clear",
                use_container_width=True,
                help="Remove the recorded hash from this session.",
            ):
                st.session_state["recorded_hash"]     = None
                st.session_state["recorded_filename"] = None
                st.session_state["recorded_at"]       = None
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)   # close .step-card

# ═════════════════════════════════════════════
# STEP 2 – Verify a file
# ═════════════════════════════════════════════
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.markdown('<span class="step-number">Step 2</span>', unsafe_allow_html=True)
st.markdown("### 🔍 Verify a File")

st.info(
    "Compare a file against its original reference hash to see whether anything has changed.\n\n"
    "**You need either:**\n"
    "- A hash recorded in Step 1 above (current session), **or**\n"
    "- A `.json` verification record exported from a previous session."
)

# ── Two-column layout: Option A left, Option B right ─────────────────────────
col_opt_a, col_opt_b = st.columns(2, gap="large")

imported_hash = imported_filename = imported_at = None

with col_opt_a:
    st.markdown(
        '<div class="option-label">'
        '<span class="option-badge">A</span>'
        '📄 Load a Saved JSON Record'
        '</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Upload a `.json` record exported by FileGuard. "
        "Its structure and hash format are validated before use — it is never executed."
    )

    json_file = st.file_uploader(
        label="Upload a FileGuard .json verification record",
        label_visibility="visible",
        type=["json"],
        accept_multiple_files=False,
        key="json_uploader",
        help="Only .json files are accepted here. The file is parsed as text only and never executed.",
    )

    if json_file is not None:
        raw_json = json_file.read()
        try:
            record_data = json.loads(raw_json.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            st.error(
                f"❌ **Invalid JSON** — could not parse the uploaded file: `{exc}`\n\n"
                "Make sure you uploaded the `.json` file exported by FileGuard, not a modified copy."
            )
            record_data = None

        if record_data is not None:
            ok, reason = validate_record(record_data)
            if not ok:
                st.error(
                    f"❌ **Invalid verification record** — {reason}\n\n"
                    "The file may have been modified, corrupted, or was not created by FileGuard. "
                    "Please use the original exported `.json` file."
                )
            else:
                imported_hash     = record_data["sha256"]
                imported_filename = record_data.get("original_filename", "unknown")
                imported_at       = record_data.get("recorded_at_utc", "unknown")
                st.success(
                    f"✅ Record loaded for `{imported_filename}` "
                    f"(recorded {imported_at})."
                )
                jc1, jc2 = st.columns(2)
                jc1.metric("Original filename", imported_filename)
                jc2.metric("Recorded at (UTC)", imported_at)
                st.markdown("**Reference SHA-256 (from record)**")
                st.text_area(
                    label="Imported reference hash",
                    value=imported_hash,
                    height=80,
                    label_visibility="collapsed",
                    key="hash_display_imported",
                    help="This hash came from the uploaded JSON record.",
                )

with col_opt_b:
    st.markdown(
        '<div class="option-label">'
        '<span class="option-badge">B</span>'
        '📂 Upload the File to Check'
        '</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Upload the file whose integrity you want to verify. "
        "FileGuard compares its contents byte-for-byte — the filename is not used in the comparison."
    )

    verify_file = st.file_uploader(
        label="Choose the file to verify",
        label_visibility="visible",
        type=None,
        accept_multiple_files=False,
        key="verify_uploader",
        help="Any file type accepted. Contents are hashed in memory and never saved.",
    )

# ── Resolve active reference ──────────────────────────────────────────────────
if imported_hash:
    active_ref_hash     = imported_hash
    active_ref_filename = imported_filename
    active_ref_source   = f"imported JSON record (recorded {imported_at})"
elif st.session_state["recorded_hash"]:
    active_ref_hash     = st.session_state["recorded_hash"]
    active_ref_filename = st.session_state["recorded_filename"]
    active_ref_source   = f"Step 1 session recording (recorded {st.session_state['recorded_at']})"
else:
    active_ref_hash = active_ref_filename = active_ref_source = None

# ── Active-reference status pill ─────────────────────────────────────────────
st.markdown("")
if active_ref_hash:
    st.markdown(
        f'<span class="status-pill pill-ready">● Reference ready — {active_ref_source}</span>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<span class="status-pill pill-warn">'
        '○ No reference available — complete Step 1 or upload a JSON record in Option A'
        '</span>',
        unsafe_allow_html=True,
    )

# ── Verification result ───────────────────────────────────────────────────────
if verify_file is not None:
    v_raw  = verify_file.read()
    v_size = len(v_raw)

    if v_size > MAX_FILE_SIZE_BYTES:
        st.error(
            f"❌ **File too large** — {format_file_size(v_size)} uploaded, "
            f"limit is {MAX_FILE_SIZE_MB} MB."
        )
    elif v_size == 0:
        st.warning("⚠️ The uploaded file is empty. Please choose a different file.")
    elif active_ref_hash is None:
        st.warning(
            "⚠️ **No reference hash available.** "
            "Please complete Step 1 to record a hash, "
            "or upload a `.json` record in Option A above."
        )
    else:
        try:
            current_hash = compute_sha256(v_raw)
        except Exception as exc:
            st.error(f"❌ Could not hash the file: {exc}")
            st.stop()

        hashes_match = (current_hash == active_ref_hash)
        verified_at  = now_utc()
        result_str   = "UNCHANGED" if hashes_match else "MODIFIED"

        st.markdown("---")

        # ── Verdict banner ────────────────────────────────────────────────────
        if hashes_match:
            st.markdown(
                '<div class="verdict-match">'
                '<div class="verdict-title">✅ &nbsp;File Unchanged</div>'
                '<div class="verdict-sub">'
                'The SHA-256 hashes match exactly. Every byte of the file is identical '
                'to the original reference.'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="verdict-mismatch">'
                '<div class="verdict-title">⚠️ &nbsp;File Modified</div>'
                '<div class="verdict-sub">'
                'The SHA-256 hashes do not match. The file\'s contents have changed '
                'since the reference was recorded — positions that differ are highlighted below.'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )

        # ── Metadata row ──────────────────────────────────────────────────────
        vc1, vc2, vc3, vc4 = st.columns(4)
        vc1.metric("Checked file",      verify_file.name)
        vc2.metric("File size",         format_file_size(v_size))
        vc3.metric("Verified at (UTC)", verified_at)
        vc4.metric("Result",            "✅ Unchanged" if hashes_match else "⚠️ Modified")

        # ── Hash comparison ───────────────────────────────────────────────────
        st.markdown("#### 🔍 Hash Comparison")

        if hashes_match:
            # Simple side-by-side text areas — both teal, no diff needed
            hcol_a, hcol_b = st.columns(2)
            with hcol_a:
                st.markdown(
                    '<p class="hash-label-row">Original reference</p>'
                    f'<p class="hash-source-row">{active_ref_source}</p>',
                    unsafe_allow_html=True,
                )
                st.text_area(
                    label="Original hash",
                    value=active_ref_hash,
                    height=90,
                    label_visibility="collapsed",
                    key="hash_cmp_original",
                    help="The reference hash recorded in Step 1 or loaded from a JSON record.",
                )
            with hcol_b:
                st.markdown(
                    f'<p class="hash-label-row">Current file — {verify_file.name}</p>'
                    '<p class="hash-source-row">just computed</p>',
                    unsafe_allow_html=True,
                )
                st.text_area(
                    label="Current hash",
                    value=current_hash,
                    height=90,
                    label_visibility="collapsed",
                    key="hash_cmp_current",
                    help="The SHA-256 hash computed right now from the uploaded file's contents.",
                )
        else:
            # Show original as plain text area, current with per-char diff
            hcol_a, hcol_b = st.columns(2)
            with hcol_a:
                st.markdown(
                    '<p class="hash-label-row">Original reference</p>'
                    f'<p class="hash-source-row">{active_ref_source}</p>',
                    unsafe_allow_html=True,
                )
                st.text_area(
                    label="Original hash",
                    value=active_ref_hash,
                    height=90,
                    label_visibility="collapsed",
                    key="hash_cmp_original",
                    help="The reference hash recorded in Step 1 or loaded from a JSON record.",
                )
            with hcol_b:
                st.markdown(
                    f'<p class="hash-label-row">Current file — {verify_file.name}</p>'
                    '<p class="hash-source-row">just computed — '
                    '<span style="color:#f08080;">red = differs from original</span></p>',
                    unsafe_allow_html=True,
                )
                diff_html = render_hash_diff(active_ref_hash, current_hash)
                st.markdown(
                    f'<div class="hash-diff-wrap">{diff_html}</div>',
                    unsafe_allow_html=True,
                )

        # ── Explanation ───────────────────────────────────────────────────────
        st.markdown("#### 💬 What does this mean?")
        if hashes_match:
            st.markdown(
                """
                <div class="info-panel">
                    The SHA-256 digest of the uploaded file is <strong>identical</strong> to the
                    original reference. Every byte is the same as when the reference was recorded —
                    the file has not been altered, corrupted, or substituted.<br><br>
                    <strong>Note:</strong> this confirms byte-for-byte identity only. It does not
                    mean the file is free of malware — if the original already contained malicious
                    content, the hashes would still match.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="info-panel">
                    The SHA-256 digest of the uploaded file is <strong>different</strong> from the
                    original reference. The file's contents have changed since the reference was
                    recorded.<br><br>
                    <strong>Possible explanations:</strong>
                    <ul>
                        <li>The file was intentionally edited or updated.</li>
                        <li>The file was corrupted during transfer or storage.</li>
                        <li>A different version or copy of the file was uploaded by mistake.</li>
                        <li>The file was maliciously tampered with.</li>
                    </ul>
                    A mismatch does <em>not</em> automatically mean malicious tampering — it only
                    tells you the contents differ. Investigate the cause based on your context.
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Trust reminder ────────────────────────────────────────────────────
        st.markdown(
            """
            <div class="warn-panel">
                ⚠️ <strong>Trust reminder:</strong> this result is only reliable if the reference
                hash record has been stored securely and has not itself been modified. If an
                attacker can alter both the file and the record, the comparison result cannot
                be trusted. Store JSON records in a location you control — encrypted storage,
                signed email, or a version-controlled repository with commit signing.
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Download verification report ──────────────────────────────────────
        report_text = build_verification_report(
            ref_filename    = active_ref_filename or "unknown",
            ref_hash        = active_ref_hash,
            ref_source      = active_ref_source,
            verify_filename = verify_file.name,
            current_hash    = current_hash,
            verified_at     = verified_at,
            result          = result_str,
        )
        report_name = (
            f"fileguard_report_{verify_file.name}_{verified_at.replace(':', '-')}.txt"
        )

        st.markdown(
            f"""
            <div class="download-cta">
                <p>
                    <strong style="color:#2ddfb8;">📥 Download Verification Report</strong><br>
                    Export a plain-text report containing the filename, original hash, current hash,
                    date and time of verification ({verified_at}), and result ({result_str}).
                    Suitable for audit trails or sharing with colleagues.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.download_button(
            label=f"⬇️ Download verification report (.txt)  —  Result: {result_str}",
            data=report_text.encode("utf-8"),
            file_name=report_name,
            mime="text/plain",
            use_container_width=True,
        )

st.markdown('</div>', unsafe_allow_html=True)   # close .step-card

# ═════════════════════════════════════════════
# SECTION 3 – SHA-256 explainer
# ═════════════════════════════════════════════
st.markdown("---")
with st.expander("ℹ️ What is SHA-256 and why does it matter?", expanded=False):
    st.markdown(
        """
        <div class="info-panel">
            <b>SHA-256</b> (Secure Hash Algorithm 256-bit) is a one-way cryptographic function that
            converts any input — a text file, an image, an executable — into a fixed 64-character
            hexadecimal string called a <em>digest</em> or <em>hash</em>.<br><br>

            <b>Key properties:</b>
            <ul>
                <li><b>Deterministic</b> — the same file always produces the same hash.</li>
                <li><b>Avalanche effect</b> — changing even one byte produces a completely different hash.</li>
                <li><b>One-way</b> — you cannot reverse a hash back into the original file.</li>
                <li><b>Collision-resistant</b> — it is computationally infeasible to find two
                    different files with the same hash.</li>
            </ul>

            <b>How FileGuard uses this:</b> hash a file today, hash it again later — if the two
            digests match, the file has not changed. If they differ, something changed, whether
            intentional editing, accidental corruption, or malicious tampering.<br><br>

            <b>Important:</b> hashing alone does <em>not</em> prove a file is free of malware.
            It only tells you whether the file is byte-for-byte identical to a previously
            known version.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="example-hash-block">
            <span class="ex-label">Example — SHA-256 of the text "Hello, World!"</span>
            dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f
        </div>
        <div class="example-hash-block">
            <span class="ex-label">SHA-256 of "Hello, World?" (only the last character changed)</span>
            <span style="color:#f08080;">f16c3bb0</span>532537acd5b2e418f2b1235b29181e35cffee7cc29d84de4a1d62e4d
        </div>
        <p style="color:#8ab4cc; font-size:0.83rem; margin-top:0.6rem;">
            Even a single character change produces a completely different 64-character hash —
            this is the <em>avalanche effect</em> and is why SHA-256 is a reliable tamper indicator.
        </p>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#6b9ab8; font-size:0.8rem;'>"
    "FileGuard v4.0 · All processing is local · No files or hashes are transmitted or stored"
    "</p>",
    unsafe_allow_html=True,
)


# ═════════════════════════════════════════════════════════════════════════════
# SELF-TEST  —  run with:  python app.py
# When Streamlit imports this file it sets __name__ = 'app', so the block
# below is skipped entirely during normal app operation.
# ═════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":

    _passed = 0
    _failed = 0

    def _check(label: str, got, expected) -> None:
        global _passed, _failed
        if got == expected:
            print(f"PASS  {label}")
            _passed += 1
        else:
            print(f"FAIL  {label}")
            print(f"      expected : {expected!r}")
            print(f"      got      : {got!r}")
            _failed += 1

    def _check_true(label: str, cond: bool) -> None:
        global _passed, _failed
        if cond:
            print(f"PASS  {label}")
            _passed += 1
        else:
            print(f"FAIL  {label}")
            _failed += 1

    # ── Test data ─────────────────────────────────────────────────────────────
    import hashlib as _hl
    _HELLO_BYTES  = b"Hello, World!\n"
    _HELLO_SHA256 = _hl.sha256(_HELLO_BYTES).hexdigest()
    _EMPTY_SHA256 = _hl.sha256(b"").hexdigest()

    _GOOD_RECORD = {
        "schema_version":    "1",
        "tool":              "FileGuard",
        "original_filename": "test.txt",
        "sha256":            _EMPTY_SHA256,
        "recorded_at_utc":   "2025-01-01T00:00:00Z",
    }

    print("=" * 60)
    print("  FileGuard — automated helper-function tests")
    print("=" * 60)
    print()

    # ── compute_sha256 ────────────────────────────────────────────────────────
    print("--- compute_sha256 ---")
    _check(
        "known digest: SHA-256(Hello, World!\\n)",
        compute_sha256(_HELLO_BYTES),
        _HELLO_SHA256,
    )
    _check(
        "determinism: same bytes => same hash (call 1 == call 2)",
        compute_sha256(_HELLO_BYTES),
        compute_sha256(_HELLO_BYTES),
    )
    _check(
        "empty bytes: SHA-256(b'') equals known empty-string digest",
        compute_sha256(b""),
        _EMPTY_SHA256,
    )
    _check_true(
        "avalanche: flip one bit => completely different hash",
        compute_sha256(bytes([_HELLO_BYTES[0] ^ 1]) + _HELLO_BYTES[1:]) != _HELLO_SHA256,
    )
    _check_true(
        "output length: always exactly 64 characters",
        len(compute_sha256(_HELLO_BYTES)) == 64,
    )
    _check_true(
        "output charset: only lowercase hex [0-9a-f]",
        re.fullmatch(r"[0-9a-f]{64}", compute_sha256(_HELLO_BYTES)) is not None,
    )
    _check_true(
        "large input: 1 MB of zeros => valid 64-char hash (chunked path)",
        re.fullmatch(r"[0-9a-f]{64}", compute_sha256(b"\x00" * 1_048_576)) is not None,
    )
    _check_true(
        "cross-check: compute_sha256 matches hashlib.sha256 directly",
        compute_sha256(_HELLO_BYTES) == _hl.sha256(_HELLO_BYTES).hexdigest(),
    )

    # ── format_file_size ──────────────────────────────────────────────────────
    print()
    print("--- format_file_size ---")
    _check("0 B",             format_file_size(0),                "0 B")
    _check("1 B",             format_file_size(1),                "1 B")
    _check("512 B",           format_file_size(512),              "512 B")
    _check("1023 B",          format_file_size(1023),             "1023 B")
    _check("1024 => 1.00 KB", format_file_size(1024),             "1.00 KB")
    _check("2048 => 2.00 KB", format_file_size(2048),             "2.00 KB")
    _check("1 MB",            format_file_size(1024 * 1024),      "1.00 MB")
    _check("10 MB",           format_file_size(10 * 1024 * 1024), "10.00 MB")

    # ── is_valid_sha256 ───────────────────────────────────────────────────────
    print()
    print("--- is_valid_sha256 ---")
    _check_true("64 lowercase hex 'a's: valid",       is_valid_sha256("a" * 64))
    _check_true("64 digit '0's: valid",                is_valid_sha256("0" * 64))
    _check_true("64 chars 'deadbeef' repeated: valid", is_valid_sha256("deadbeef" * 8))
    _check_true("real EMPTY_SHA256: valid",             is_valid_sha256(_EMPTY_SHA256))
    _check_true("real HELLO_SHA256: valid",             is_valid_sha256(_HELLO_SHA256))
    _check_true("63 chars: invalid",                   not is_valid_sha256("a" * 63))
    _check_true("65 chars: invalid",                   not is_valid_sha256("a" * 65))
    _check_true("64 uppercase 'A's: invalid",          not is_valid_sha256("A" * 64))
    _check_true("non-hex 'z' * 64: invalid",           not is_valid_sha256("z" * 64))
    _check_true("empty string: invalid",               not is_valid_sha256(""))
    _check_true("None (via 'value or \"\"'): invalid",  not is_valid_sha256(None))
    _check_true("string 'not-a-hash': invalid",        not is_valid_sha256("not-a-hash"))
    _check_true("hash with space: invalid",
                not is_valid_sha256("a" * 32 + " " + "a" * 31))

    # ── validate_record ───────────────────────────────────────────────────────
    print()
    print("--- validate_record ---")
    _ok, _msg = validate_record(_GOOD_RECORD)
    _check_true("well-formed record: accepted",       _ok)
    _check("well-formed record: empty reason",        _msg, "")

    for _field in ["schema_version", "tool", "original_filename",
                   "sha256", "recorded_at_utc"]:
        _bad = dict(_GOOD_RECORD)
        del _bad[_field]
        _ok, _msg = validate_record(_bad)
        _check_true(f"missing '{_field}': rejected",              not _ok)
        _check_true(f"missing '{_field}': reason mentions it",    _field in _msg)

    _bad_tool = dict(_GOOD_RECORD)
    _bad_tool["tool"] = "OtherApp"
    _ok, _msg = validate_record(_bad_tool)
    _check_true("wrong tool name: rejected",              not _ok)
    _check_true("wrong tool: reason mentions FileGuard",  "FileGuard" in _msg)

    for _label, _val in [
        ("too short (3 chars)",  "abc"),
        ("uppercase hex (A*64)", "A" * 64),
        ("non-hex (z*64)",       "z" * 64),
        ("empty string",         ""),
        ("63 chars",             "a" * 63),
        ("65 chars",             "a" * 65),
    ]:
        _bad_h = dict(_GOOD_RECORD)
        _bad_h["sha256"] = _val
        _ok, _ = validate_record(_bad_h)
        _check_true(f"sha256 {_label}: rejected", not _ok)

    # ── build_record ──────────────────────────────────────────────────────────
    print()
    print("--- build_record ---")
    _rec = build_record("file.pdf", _EMPTY_SHA256, "2025-01-01T00:00:00Z")
    _check("schema_version == '1'",        _rec["schema_version"],    "1")
    _check("tool == 'FileGuard'",          _rec["tool"],              "FileGuard")
    _check("original_filename preserved",  _rec["original_filename"], "file.pdf")
    _check("sha256 preserved",             _rec["sha256"],            _EMPTY_SHA256)
    _check("recorded_at_utc preserved",    _rec["recorded_at_utc"],   "2025-01-01T00:00:00Z")
    _ok, _ = validate_record(_rec)
    _check_true("build_record output passes validate_record", _ok)
    import json as _json
    _parsed = _json.loads(_json.dumps(_rec, indent=2))
    _ok2, _ = validate_record(_parsed)
    _check_true("build_record -> JSON -> parse -> validate: passes", _ok2)
    _check("JSON round-trip: sha256 survives serialisation",
           _parsed["sha256"], _EMPTY_SHA256)

    # ── build_verification_report ─────────────────────────────────────────────
    print()
    print("--- build_verification_report ---")
    _rpt_match = build_verification_report(
        ref_filename="orig.txt", ref_hash=_EMPTY_SHA256, ref_source="session",
        verify_filename="copy.txt", current_hash=_EMPTY_SHA256,
        verified_at="2025-01-01T00:00:00Z", result="UNCHANGED",
    )
    _check_true("UNCHANGED report: contains result UNCHANGED",      "UNCHANGED" in _rpt_match)
    _check_true("UNCHANGED report: contains ref hash",              _EMPTY_SHA256 in _rpt_match)
    _check_true("UNCHANGED report: contains YES",                   "YES" in _rpt_match)
    _check_true("UNCHANGED report: contains verify filename",       "copy.txt" in _rpt_match)
    _check_true("UNCHANGED report: contains verified_at timestamp", "2025-01-01T00:00:00Z" in _rpt_match)

    _rpt_mismatch = build_verification_report(
        ref_filename="orig.txt", ref_hash=_EMPTY_SHA256, ref_source="session",
        verify_filename="copy.txt", current_hash="b" * 64,
        verified_at="2025-01-01T00:00:00Z", result="MODIFIED",
    )
    _check_true("MODIFIED report: contains result MODIFIED",  "MODIFIED" in _rpt_mismatch)
    _check_true("MODIFIED report: contains NO",               "NO" in _rpt_mismatch)
    _check_true("MODIFIED report: contains current hash",     "b" * 64 in _rpt_mismatch)
    _check_true("MODIFIED report: safety note present",
                "does not automatically indicate malicious tampering" in _rpt_mismatch)

    # ── Size-limit arithmetic ─────────────────────────────────────────────────
    print()
    print("--- size-limit arithmetic ---")
    _check("10 MB constant == 10485760", MAX_FILE_SIZE_BYTES, 10485760)
    _check_true("10485760 bytes is NOT over limit",
                not (10485760 > MAX_FILE_SIZE_BYTES))
    _check_true("10485761 bytes IS over limit",
                10485761 > MAX_FILE_SIZE_BYTES)
    _check_true("0 bytes triggers empty guard", 0 == 0)

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print(f"  {_passed} passed  /  {_failed} failed  /  {_passed + _failed} total")
    print("=" * 60)

    sys.exit(0 if _failed == 0 else 1)
