# LinguaAI — Language Translator

## Folder Structure (IMPORTANT — must match exactly)

```
TranslateX/
│
├── fastapi_server.py       ← FastAPI backend (port 8000)
├── flask_app.py            ← Flask frontend (port 5000)
├── requirements.txt        ← All dependencies
├── README.md
│
└── templates/              ← Flask looks here for HTML
    └── index.html          ← The UI page
```

---

## Setup & Run

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Start FastAPI  (open Terminal 1)
```bash
python fastapi_server.py
```
✅ You should see: `http://localhost:8000`
📖 Swagger API docs: `http://localhost:8000/docs`

### Step 3 — Start Flask  (open Terminal 2)
```bash
python flask_app.py
```
✅ You should see: `http://localhost:5000`

### Step 4 — Open Browser
```
http://localhost:5000
```

---

## FastAPI Endpoints

| Method | Endpoint     | Description                |
|--------|--------------|----------------------------|
| GET    | /            | Health check               |
| GET    | /languages   | All 70+ supported languages|
| POST   | /translate   | Translate text             |
| POST   | /detect      | Detect language of text    |
| GET    | /docs        | Auto-generated Swagger UI  |

### Example: POST /translate
```json
{
  "text": "Hello, how are you?",
  "dest": "fr",
  "src": "auto"
}
```

### Example: POST /detect
```json
{
  "text": "Bonjour le monde"
}
```

---

## Features
- 70+ languages
- Auto language detection
- Swap source/target
- Translation history (last 5)
- Copy to clipboard
- Ctrl+Enter shortcut
- FastAPI Swagger UI
- Live API status in UI
