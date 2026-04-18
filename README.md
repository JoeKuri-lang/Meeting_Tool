# 📋 Meeting Notes Tool

A CrewAI-powered app that turns messy meeting notes, PDFs, or documents into clean, stakeholder-ready summaries — with action items pulled out automatically.

Built for teams where meetings run long, go off-topic, or produce walls of text nobody wants to read.

---
## Link to Official Site:
https://claritysync-meeting-helper.onrender.com/ 

---
## What It Does

- **Summarizes** meeting notes into concise, readable recaps
- **Extracts action items** so nothing gets lost in the noise
- **Accepts docs, PDFs, or raw text** as input
- **Outputs a clean stakeholder document** anyone can read without context
- **Streamlit UI** with API key config in the sidebar — no `.env` file required for casual use

---

## Tech Stack

| Tool | Purpose |
|---|---|
| [CrewAI](https://crewai.com) | AI agent orchestration |
| [Streamlit](https://streamlit.io) | Web UI |
| [uv](https://github.com/astral-sh/uv) | Fast Python package manager |
| Docker | Optional containerized deployment |

---

## Project Structure

```
meeting-notes-tool/
├── app.py               # Streamlit entry point
├── crew/
│   ├── agents.py        # CrewAI agent definitions
│   └── tasks.py         # Task definitions
├── utils/
│   └── parser.py        # Doc/PDF input handling
├── Dockerfile           # Docker deployment config
├── pyproject.toml       # Project dependencies (uv)
├── .env.example         # Example env vars (copy to .env)
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) installed
- An OpenAI (or compatible) API key

### 1. Clone the repo

```bash
git clone https://github.com/yourname/meeting-notes-tool.git
cd meeting-notes-tool
```

### 2. Create and activate a virtual environment

```bash
uv venv --python 3.12
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser. Enter your API key in the **sidebar** — no config file needed.

---

## API Key Setup

### Option A — Streamlit Sidebar (easiest)

Enter your API key directly in the app sidebar. It's stored only for your session.

### Option B — Environment Variable

Copy the example env file and fill it in:

```bash
cp .env.example .env
```

```env
OPENAI_API_KEY=your-key-here
```

---

## Docker Deployment

Build and run with API key passed as an environment variable:

```bash
docker build -t meeting-notes-tool .

docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your-key-here \
  meeting-notes-tool
```

Then visit [http://localhost:8501](http://localhost:8501).

---

## Contributing

PRs welcome. Open an issue first for major changes.

---

## License

MIT