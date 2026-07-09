/* ── AI Reviewer — API & Shared Utilities ──────────────────────
   API Base URL — HuggingFace Space
   ─────────────────────────────────────────────────────────── */

const API_BASE = "https://morefaat69-ai-project-review.hf.space";

/* ── Storage helpers (localStorage) ─────────────────────────── */
const Store = {
    getSessions() {
        return JSON.parse(localStorage.getItem("ai_reviewer_sessions") || "[]");
    },
    saveSession(session) {
        const sessions = Store.getSessions();
        sessions.unshift(session);          // newest first
        localStorage.setItem("ai_reviewer_sessions", JSON.stringify(sessions));
    },
    deleteSession(sessionId) {
        const sessions = Store.getSessions().filter(s => s.session_id !== sessionId);
        localStorage.setItem("ai_reviewer_sessions", JSON.stringify(sessions));
    },
    getCurrentSession() {
        return JSON.parse(sessionStorage.getItem("current_session") || "null");
    },
    setCurrentSession(session) {
        sessionStorage.setItem("current_session", JSON.stringify(session));
    },
    clearCurrentSession() {
        sessionStorage.removeItem("current_session");
    }
};

/* ── API calls ───────────────────────────────────────────────── */
const API = {
    /** POST /AI — upload file, returns { session_id, analysis, content_type, filename } */
    async analyze(file) {
        const form = new FormData();
        form.append("file", file);

        let res;
        try {
            res = await fetch(`${API_BASE}/AI`, { method: "POST", body: form });
        } catch (networkErr) {
            throw new Error(`Network error — is the HuggingFace Space running? (${networkErr.message})`);
        }

        if (!res.ok) {
            let errMsg = `HTTP ${res.status}`;
            try {
                const errBody = await res.json();
                errMsg = errBody.error || JSON.stringify(errBody);
            } catch { /* ignore parse error */ }
            throw new Error(errMsg);
        }

        const data = await res.json();
        return data;
    },

    /** POST /chat — send follow-up message */
    async chat(sessionId, message) {
        const res = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId, message })
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || `HTTP ${res.status}`);
        }
        return res.json();
    },

    /** DELETE /session/:id */
    async deleteSession(sessionId) {
        const res = await fetch(`${API_BASE}/session/${sessionId}`, { method: "DELETE" });
        return res.ok;
    },

    /** GET /health */
    async health() {
        const res = await fetch(`${API_BASE}/health`);
        return res.json();
    }
};

/* ── Toast notification ──────────────────────────────────────── */
function showToast(message, type = "success") {
    const toast = document.getElementById("toast");
    if (!toast) return;
    toast.textContent = message;
    toast.className = `show ${type}`;
    setTimeout(() => { toast.className = ""; }, 3000);
}

/* ── Loading overlay ─────────────────────────────────────────── */
function showLoading(text = "Agent is analyzing...") {
    const overlay = document.getElementById("loading-overlay");
    if (!overlay) return;
    const label = overlay.querySelector("#loading-text");
    if (label) label.textContent = text;
    overlay.classList.remove("hidden");
}

function hideLoading() {
    const overlay = document.getElementById("loading-overlay");
    if (overlay) overlay.classList.add("hidden");
}

/* ── Navigation helper ───────────────────────────────────────── */
function navigateTo(page) {
    window.location.href = page;
}

/* ── Simple markdown → HTML renderer ────────────────────────── */
function renderMarkdown(text) {
    return text
        // headers
        .replace(/^## (.+)$/gm, "<h2>$1</h2>")
        .replace(/^### (.+)$/gm, "<h3>$1</h3>")
        .replace(/^# (.+)$/gm, "<h2>$1</h2>")
        // bold
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        // inline code
        .replace(/`([^`]+)`/g, "<code>$1</code>")
        // code blocks
        .replace(/```[\w]*\n([\s\S]*?)```/g, "<pre><code>$1</code></pre>")
        // bullet lists
        .replace(/^\s*[-•]\s+(.+)$/gm, "<li>$1</li>")
        .replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>")
        // line breaks
        .replace(/\n{2,}/g, "</p><p>")
        .replace(/\n/g, "<br>")
        // wrap in paragraphs
        .replace(/^(?!<[hupol])/gm, "")
        // cleanup
        .replace(/<\/ul>\s*<ul>/g, "");
}
