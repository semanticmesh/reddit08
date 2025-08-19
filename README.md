# CRE Intelligence Platform

A sophisticated Commercial Real Estate (CRE) Intelligence Platform that gathers and analyzes intelligence from Reddit and social media sources.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/reddit08.git
cd reddit08

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Edit .env with your API keys

# Start the FastAPI server
uvicorn src.mcp.fastapi_app.main:app --reload --port 8000

# Access API documentation
# Open http://localhost:8000/docs in your browser
```

## Project Structure

```
reddit08/
├── src/                    # Source code
│   ├── mcp/               # MCP server implementations
│   │   ├── fastapi_app/   # FastAPI-based MCP server
│   │   ├── native_server/ # Native WebSocket MCP server
│   │   └── utils/         # Shared utilities
│   ├── scripts/           # Utility scripts
│   └── tests/             # Test suites
├── docs/                  # Comprehensive documentation
│   └── README.md          # Full documentation
├── .gitignore            # Git ignore rules
└── requirements.txt      # Python dependencies
```

## Core Features

Six intelligence techniques for comprehensive CRE analysis:

1. **Iterative JSON Refinement** - Optimizes Apify Actor payloads
2. **TF-IDF Phrase Mining** - Extracts domain-specific terminology
3. **Client-Side Filtering** - 6-stage quality control pipeline
4. **Local-Sub Targeting** - Geographic subreddit discovery
5. **Vertical Specialization** - Market segment analysis
6. **Dual-Sort Strategy** - Comprehensive coverage with backfill

## Documentation

For detailed documentation, including:
- Installation guide
- Configuration
- API usage
- Deployment instructions
- Troubleshooting

See [docs/README.md](./docs/README.md)

## Development

### Running Tests

```bash
# Run all tests
pytest src/tests/

# Run with coverage
pytest src/tests/ --cov=src
```

### Code Formatting

```bash
# Format code
black src/
isort src/

# Run linters
flake8 src/
mypy src/
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*For more detailed information, please refer to the [full documentation](./docs/README.md).*
