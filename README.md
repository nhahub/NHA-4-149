# AI Reviewer — Frontend
Connected to: https://morefaat69-ai-project-review.hf.space

## Project Structure

```
ai-reviewer/
├── page1.html        → Upload page  (drag & drop → POST /AI)
├── page2.html        → Results page (shows analysis + chat → POST /chat)
├── page3.html        → History page (localStorage + DELETE /session/:id)
│
├── css/
│   └── styles.css    → Shared styles (glass cards, toast, loading, chat bubbles)
│
└── js/
    └── api.js        → API calls, localStorage helpers, toast, markdown renderer
```

## How Pages Connect

| Page | API Endpoint | What it does |
|------|-------------|--------------|
| page1.html | POST /AI | Uploads file, gets analysis + session_id |
| page2.html | POST /chat | Sends follow-up messages using session_id |
| page3.html | DELETE /session/:id | Deletes session from API and localStorage |

## How to Run Locally
Just open `page1.html` in any browser — no server needed.
All API calls go to HuggingFace Spaces directly.

## Data Flow
1. User uploads file on page1 → API returns { session_id, analysis, content_type, filename }
2. Session saved to localStorage (history) AND sessionStorage (current)
3. page2 reads from sessionStorage → shows analysis + enables chat
4. page3 reads from localStorage → shows all past sessions
5. "View" on page3 → loads session into sessionStorage → goes to page2
6. "Delete" on page3 → calls DELETE /session/:id + removes from localStorage
