# Infer RCA

![Infer CLI Demo](demo/demov2.gif)

**Infer** is an agentic, globally installed CLI tool that acts as a local debugging assistant. It parses messy server logs, dynamically isolates the exact file causing the crash, and generates root cause analyses and fixes using a **Dual-Agent LLM Architecture** powered by Groq (Llama-3).

It features a local **ChromaDB Vector Database** to cache previously solved errors, ensuring instant responses for recurring bugs without wasting API tokens or experiencing latency.

## Features

* **Dual-Agent Architecture:** 
    * **Agent 1 (Router):** Uses a lightning-fast Groq 8B model in JSON-mode to read the log tail and accurately extract the failing file and line number across *any* programming language.
  * **Agent 2 (Debugger):** Uses a heavy Groq 70B reasoning model to ingest the *entire* source code file, finding interrelated bugs (like missing imports or bad data state) rather than just looking at isolated lines.
* **Log Tail Strategy:** Optimizes token usage and speed by automatically targeting the most recent crash at the bottom of massive production logs.
* **Local Memory Bank:** Caches stack traces and AI-generated solutions in a local ChromaDB vector database. If an error happens twice, the solution loads instantly (0 latency).
* **Beautiful Terminal UI:** Uses the `rich` library to render syntax-highlighted code blocks, loading animations, and Markdown-formatted AI responses.

## 🛠️ Technology Stack

* **Language:** Python
* **LLM Engine:** Groq API (`llama-3.1-8b-instant`, `llama-3.3-70b-versatile`)
* **Vector Database & Embeddings:** ChromaDB & Google Gemini Embeddings (`langchain-chroma`, `langchain-google-genai`)
* **User Interface:** Rich (`rich`)

## Installation & Setup

**1. Clone the repository:**
```bash
git clone https://github.com/icarus5851/infer-rca.git
cd infer-rca
```

**2. Set up a Virtual Environment (Recommended):**
```bash
python -m venv venv
source venv/Scripts/activate # On Windows
```

**3. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**4. Set up your Environment Variables:**
Create a `.env` file in the root directory like the `.env.example`. You will need a free Groq API key for text generation and a Gemini API key for local vector embeddings.
```text
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

**5. Install Globally:**
Install the tool as a global CLI command on your system:
```bash
pip install -e .
```

## Usage

Once installed globally, you can run `infer` from any directory on your machine to analyze a broken log file.

```bash
infer path/to/your/server.log
```