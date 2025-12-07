# Project Structure

## Clean, Organized Repository

```
finops-genai-agent/
│
├── 📱 Core Application Files
│   ├── streamlit_app.py              # Main Streamlit application
│   ├── intelligent_agent.py          # Smart AWS service detection
│   ├── enhanced_agent.py             # Production agent with DuckDB
│   └── analytics_dashboard.py        # Usage analytics dashboard
│
├── 📁 Configuration Files
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Environment variables template
│   ├── .gitignore                    # Git ignore rules
│   ├── Dockerfile                    # Container image
│   └── docker-compose.yml            # Docker orchestration
│
├── 🚀 Quick Start Scripts
│   ├── start.sh                      # macOS/Linux startup
│   └── start.bat                     # Windows startup
│
├── 📂 sql/                           # SQL Query Templates
│   ├── athena_architecture_inference.sql
│   └── athena_tagging_correlation.sql
│
├── 🛠️ scripts/                       # Utility Scripts
│   ├── setup_aws.py                  # AWS infrastructure setup
│   ├── setup.sh                      # Environment setup (Unix)
│   ├── setup.bat                     # Environment setup (Windows)
│   └── generate_sample_data.py       # Test data generator
│
├── 📊 sample_data/                   # Sample CSV Files
│   ├── sample_architecture_data.csv
│   ├── sample_cost_analysis.csv
│   └── sample_tagging_data.csv
│
├── 📚 docs/                          # Documentation
│   ├── README.md                     # Documentation index
│   │
│   ├── Getting Started/
│   │   ├── QUICKSTART.md
│   │   ├── RUN_LOCALLY.md
│   │   └── GET_AWS_CREDENTIALS.md
│   │
│   ├── Setup Guides/
│   │   ├── VIRTUAL_ENV_GUIDE.md
│   │   ├── VENV_QUICK_REFERENCE.md
│   │   └── AWS_CLI_SETUP.md
│   │
│   ├── Features/
│   │   ├── README_STREAMLIT.md
│   │   ├── INTELLIGENT_AGENT.md
│   │   ├── ENHANCEMENTS.md
│   │   ├── AGENT_COMPARISON.md
│   │   └── UI_GUIDE.md
│   │
│   ├── Architecture/
│   │   ├── ARCHITECTURE.md
│   │   ├── PROJECT_SUMMARY.md
│   │   └── LOGGING_ANALYTICS.md
│   │
│   ├── Deployment/
│   │   └── DEPLOYMENT.md
│   │
│   └── Support/
│       └── TROUBLESHOOTING.md
│
├── 🔧 .github/                       # GitHub Configuration
│   └── workflows/
│       └── deploy.yml                # CI/CD pipeline
│
└── 🔒 Ignored Directories (not in git)
    ├── venv/                         # Virtual environment
    ├── .vscode/                      # VS Code settings
    ├── __pycache__/                  # Python cache
    └── .streamlit/                   # Streamlit cache
```

## File Descriptions

### Core Application

| File | Purpose |
|------|---------|
| `streamlit_app.py` | Main web application with UI |
| `intelligent_agent.py` | Smart agent with service detection |
| `enhanced_agent.py` | Production agent with DuckDB (recommended) |
| `analytics_dashboard.py` | View usage statistics and patterns |

### Configuration

| File | Purpose |
|------|---------|
| `requirements.txt` | Python package dependencies |
| `.env.example` | Template for environment variables |
| `.gitignore` | Files to exclude from git |
| `Dockerfile` | Container image definition |
| `docker-compose.yml` | Multi-container orchestration |

### Quick Start

| File | Purpose |
|------|---------|
| `start.sh` | One-command startup (macOS/Linux) |
| `start.bat` | One-command startup (Windows) |

### SQL Templates

| File | Purpose |
|------|---------|
| `sql/athena_architecture_inference.sql` | Detect architectural inefficiencies |
| `sql/athena_tagging_correlation.sql` | Find untagged resources |

### Utility Scripts

| File | Purpose |
|------|---------|
| `scripts/setup_aws.py` | Create DynamoDB table, verify Bedrock |
| `scripts/setup.sh` | Automated environment setup (Unix) |
| `scripts/setup.bat` | Automated environment setup (Windows) |
| `scripts/generate_sample_data.py` | Create test CSV files |

### Sample Data

| File | Purpose |
|------|---------|
| `sample_data/sample_architecture_data.csv` | EC2 architecture test data |
| `sample_data/sample_cost_analysis.csv` | General cost analysis data |
| `sample_data/sample_tagging_data.csv` | Tagging correlation data |

### Documentation

See [docs/README.md](docs/README.md) for complete documentation index.

## What's Not in Git

These files/folders are excluded via `.gitignore`:

- `venv/` - Virtual environment (recreate locally)
- `.env` - Your AWS credentials (keep secret!)
- `__pycache__/` - Python bytecode cache
- `.vscode/` - Editor settings
- `.streamlit/` - Streamlit cache
- `*.csv` - Uploaded data files (except sample_data/)
- `*.log` - Log files
- `.DS_Store` - macOS metadata

## Quick Navigation

### For New Users
```bash
# 1. Read main README
cat README.md

# 2. Quick start
cat docs/QUICKSTART.md

# 3. Run locally
cat docs/RUN_LOCALLY.md
```

### For Developers
```bash
# 1. Architecture
cat docs/ARCHITECTURE.md

# 2. Agent comparison
cat docs/AGENT_COMPARISON.md

# 3. Enhancements
cat docs/ENHANCEMENTS.md
```

### For DevOps
```bash
# 1. Deployment
cat docs/DEPLOYMENT.md

# 2. Logging
cat docs/LOGGING_ANALYTICS.md

# 3. CI/CD
cat .github/workflows/deploy.yml
```

## Maintenance

### Adding New Files

**Python modules:** Place in root directory
**Documentation:** Place in `docs/` with appropriate category
**SQL queries:** Place in `sql/`
**Utility scripts:** Place in `scripts/`
**Sample data:** Place in `sample_data/`

### Updating Documentation

1. Edit relevant file in `docs/`
2. Update `docs/README.md` index if needed
3. Update main `README.md` if structure changes
4. Commit with descriptive message

### Cleaning Up

```bash
# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +

# Remove log files
rm -f *.log

# Clear Streamlit cache
streamlit cache clear
```

## Benefits of This Structure

✅ **Organized** - Clear separation of concerns
✅ **Discoverable** - Easy to find what you need
✅ **Maintainable** - Simple to update and extend
✅ **Professional** - Industry-standard layout
✅ **Scalable** - Room for growth
✅ **Clean** - No clutter in root directory

## Migration Notes

### Old Structure → New Structure

| Old Location | New Location |
|--------------|--------------|
| `*.md` (docs) | `docs/*.md` |
| `athena_*.sql` | `sql/athena_*.sql` |
| `setup_aws.py` | `scripts/setup_aws.py` |
| `generate_sample_data.py` | `scripts/generate_sample_data.py` |
| `sample_*.csv` | `sample_data/sample_*.csv` |
| `genai_agent_logic.py` | ❌ Removed (obsolete) |

### Updating References

All internal references have been updated:
- ✅ README.md links
- ✅ streamlit_app.py file paths
- ✅ Documentation cross-references
- ✅ Script imports

---

**The repository is now clean, organized, and professional!** 🎯
