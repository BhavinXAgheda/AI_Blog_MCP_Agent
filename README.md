# 🤖 AI Blog MCP Agent

A local AI-powered research agent that searches the web, fetches real content, and generates grounded answers using a local Ollama model — exposed as an MCP (Model Context Protocol) tool for Claude Desktop.

---

## 🧠 How It Works

```
Query → Summarize → Generate Search Query → Tavily Search → Fetch Docs → Grounded Answer
```

| Step | Method | Description |
|------|--------|-------------|
| 1 | `summarize()` | Expands the query into context using local Ollama model |
| 2 | `make_search_query()` | Condenses query into a short search string (under 400 chars) |
| 3 | `search_web()` | Searches the web using Tavily API |
| 4 | `fetch_docs()` | Scrapes and cleans text from URLs (skips blocked domains) |
| 5 | `uni_function()` | Combines all steps and generates a final grounded answer |

---

## 🚀 Features

- 🔍 Real-time web search via [Tavily API](https://app.tavily.com)
- 🧹 Automatic content cleaning (removes scripts, navbars, footers)
- 🚫 Blocked domain filtering (Medium, YouTube, Twitter, Reddit)
- 🤖 Local LLM inference via [Ollama](https://ollama.com)
- 🔌 MCP tool integration for Claude Desktop
- 🧪 Test mode for quick pipeline validation

---

## 📦 Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally with `gpt-oss:120b-cloud` model
- Tavily API key — get one at [app.tavily.com](https://app.tavily.com)

---

## 🛠️ Installation

**1. Clone the repo:**
```bash
git clone https://github.com/BhavinXAgheda/AI_Blog_MCP_Agent.git
cd AI_Blog_MCP_Agent
```

**2. Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies:**
```bash
pip install fastmcp ollama tavily-python requests beautifulsoup4 python-dotenv
```

**4. Create `.env` file:**
```bash
cp .env.example .env
```

Then edit `.env` and add your Tavily API key:
```
TAVILY_API_KEY=your-tavily-api-key-here
```

---

## ▶️ Usage

**Test the pipeline:**
```bash
python test.py test
```

**Start as MCP server:**
```bash
python test.py
```

---

## 🔌 Claude Desktop Integration

Add this to your `claude_desktop_config.json`:

**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "blog-agent": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/AI_Blog_MCP_Agent/test.py"]
    }
  }
}
```

Replace the paths with your actual venv and project paths, then **restart Claude Desktop**.

You can then ask Claude:
> *"Research the latest AI news in March 2026"*

And it will call your local agent to search, fetch, and answer using live web data.

---

## 📁 Project Structure

```
AI_Blog_MCP_Agent/
├── test.py           # Main agent + MCP server
├── .env              # Your API keys (never committed)
├── .env.example      # Template for environment variables
├── .gitignore        # Ignores .env, venv, __pycache__
└── README.md         # This file
```

---

## 🔐 Environment Variables

| Variable | Description |
|----------|-------------|
| `TAVILY_API_KEY` | Your Tavily search API key |

---

## 🚫 Blocked Domains

The following domains are skipped during doc fetching (paywalled or JS-heavy):

- `medium.com`
- `youtube.com`
- `twitter.com`
- `reddit.com`

You can extend the `BLOCKED_DOMAINS` list in `test.py` as needed.

---

## 🧪 Example Output

```
Query:        How do I handle file uploads in Next.js 14?
Search Query: Next.js 14 file upload handling
Summary:      The user is asking for a guide on implementing file upload...
URLs:         ['https://oneuptime.com/blog/...', 'https://dev.to/...']
Docs fetched: 2
Answer:       ## Handling File Uploads in Next.js 14 ...
```

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## 🙌 Built With

- [FastMCP](https://github.com/jlowin/fastmcp) — MCP server framework
- [Ollama](https://ollama.com) — Local LLM inference
- [Tavily](https://app.tavily.com) — Web search API
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) — HTML parsing
