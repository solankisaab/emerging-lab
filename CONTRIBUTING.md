# 🤝 Contributing to AI News Aggregator

Thank you for considering a contribution! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/ai-news-aggregator.git
cd ai-news-aggregator
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your API keys
uvicorn backend.main:app --reload
```

## Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code |
| `develop` | Integration branch |
| `feature/xyz` | New features |
| `fix/xyz` | Bug fixes |

## Commit Message Format

```
feat: add semantic search endpoint
fix: resolve FAISS index loading error
docs: update RAG pipeline diagram
refactor: simplify news fetcher logic
test: add unit tests for summarizer
```

## Code Style

This project uses **Ruff** for linting and **Black** for formatting:

```bash
ruff check backend/
black backend/ tests/
```

## Running Tests

```bash
pytest tests/ -v
```

## Areas to Contribute

- 🌐 Add new news sources (RSS feeds, APIs)
- 🤖 Improve LLM prompts for better summaries
- 📊 Build evaluation metrics for RAG retrieval quality
- 🎨 Improve the frontend UI
- 🌍 Add multi-language support
- 🔔 Add notification / alert features

## Questions?

Open an issue or start a Discussion on GitHub.
