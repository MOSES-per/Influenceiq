# Ask InfluenceIQ (agent layer)

A tool-calling LLM agent on top of InfluenceIQ's analytics. The model decides which tool to call, the
code runs it, and the results go back to the model until it can answer.

## Flow
user question -> input guard -> LLM (Gemini via OpenAI-compatible API) -> tool calls -> results -> answer

## Tools
| Tool | What it does |
|---|---|
| `analyze_creator` | Collects public YouTube/Reddit data and runs the engagement, authenticity, niche and IIS scoring |
| `compare_creators` | Analyzes two creators and compares them |
| `search_knowledge` | RAG: embedding search over the scoring methodology and analyzed creators' post titles |

## RAG
Documents are embedded with `gemini-embedding-001` and stored in an in-memory vector store (cosine
similarity in NumPy). Post titles are indexed whenever a creator is analyzed.

## Safety
- Input length limit and blocking of obvious prompt-injection phrases
- Third-party text (bios, post titles) is sanitized and treated as data in the system prompt
- Emails, phone numbers and API-key-like strings are redacted from indexed text and answers
- Tool arguments are validated; tool errors are returned to the model instead of crashing
- Step limit on the agent loop; API calls retry on rate limits

## Run
```
pip install -r requirements.txt
copy .env.example .env      (then add your keys)
streamlit run influenceiq/dashboard/app.py     -> open "Ask InfluenceIQ" in the sidebar
pytest
```
Tests run offline with a fake LLM, so they need no API keys.

## Limits
Only post titles and public counts are available (no comment text). The authenticity index is a heuristic.
