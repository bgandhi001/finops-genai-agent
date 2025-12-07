# FinOps GenAI Agent Project

This repository contains the blueprints for two "Cool GenAI Projects" for a FinOps Architect, specifically tailored for scenarios where you **only have access to the Cost & Usage Report (CUR)** (via Athena) and not the customer's actual AWS account APIs.

## 🎯 How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│                      (Streamlit Web App)                            │
│                                                                     │
│  📁 Upload CSV  →  💬 Ask Questions  →  📊 View Insights          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    INTELLIGENT AGENT LAYER                          │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   Service    │  │   Column     │  │   Smart      │            │
│  │  Detection   │  │Classification│  │  Questions   │            │
│  │  (20+ AWS)   │  │  (Auto)      │  │  Generator   │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TEXT-TO-SQL ENGINE                               │
│                     (DuckDB + LLM)                                  │
│                                                                     │
│  User Query  →  LLM Generates SQL  →  Execute SQL  →  Results     │
│                                                                     │
│  Example:                                                           │
│  "Top 5 costs" → SELECT service, SUM(cost) → [Results] → Summary  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                     │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   DuckDB     │  │  AWS Bedrock │  │  DynamoDB    │            │
│  │  (Fast SQL)  │  │  (Claude 3)  │  │  (Learning)  │            │
│  │  Zero-copy   │  │  Analysis    │  │  Storage     │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

### Text-to-SQL Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: User Asks Question                                         │
│ "What are my top 5 EC2 cost drivers?"                              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: LLM Generates SQL (AWS Bedrock)                            │
│                                                                     │
│ SELECT instance_type, SUM(cost) as total_cost                      │
│ FROM aws_data                                                       │
│ WHERE service = 'EC2'                                               │
│ GROUP BY instance_type                                              │
│ ORDER BY total_cost DESC                                            │
│ LIMIT 5                                                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: SQL Sanitization & Validation                              │
│ ✅ Only SELECT allowed                                             │
│ ❌ Block DROP, DELETE, etc.                                        │
│ ✅ Verify table name                                               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: Execute SQL (DuckDB)                                       │
│ ⚡ Fast execution (0.03s for 10M rows)                            │
│ 💾 Zero-copy (queries CSV directly)                               │
│ 📊 Accurate calculations                                           │
│                                                                     │
│ Results:                                                            │
│ t3.large    → $1,234.56                                           │
│ m5.xlarge   → $987.65                                             │
│ t3.medium   → $543.21                                             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 5: LLM Summarizes Results                                     │
│                                                                     │
│ "Your top 5 EC2 cost drivers are:                                  │
│  1. t3.large instances: $1,234.56 (40%)                           │
│  2. m5.xlarge instances: $987.65 (32%)                            │
│  3. t3.medium instances: $543.21 (18%)                            │
│                                                                     │
│  💡 Recommendation: Consider Reserved Instances for t3.large       │
│  to save ~30% ($370/month)"                                        │
└─────────────────────────────────────────────────────────────────────┘
```

### Learning System Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                                 │
│                                                                     │
│  Upload File  →  Ask Question  →  Get Answer  →  View Charts      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AUTOMATIC LOGGING                                │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   Session    │  │    Query     │  │   Response   │            │
│  │   Tracking   │  │   Logging    │  │   Metrics    │            │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
│         │                  │                  │                     │
│         └──────────────────┼──────────────────┘                     │
│                            ▼                                        │
│                    ┌──────────────┐                                │
│                    │  DynamoDB    │                                │
│                    │  (90-day TTL)│                                │
│                    └──────────────┘                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PATTERN ANALYSIS                                 │
│                                                                     │
│  📊 Query Patterns    → Most common questions                      │
│  ⚡ Performance       → Slow queries identified                    │
│  🎯 Service Usage     → Popular AWS services                       │
│  💡 Success Rates     → What works best                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CONTINUOUS IMPROVEMENT                           │
│                                                                     │
│  ✅ Better Questions   → Generate smarter prompts                  │
│  ✅ Faster Responses   → Optimize SQL queries                      │
│  ✅ More Accurate      → Improve analysis                          │
│  ✅ Better UX          → Adapt to user behavior                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Learning Feedback Loop

```
    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    │  1. User asks: "Show me EC2 costs"                 │
    │     ↓                                               │
    │  2. Agent responds in 4.5s                         │
    │     ↓                                               │
    │  3. Log: query, time, success ──→ DynamoDB         │
    │     ↓                                               │
    │  4. Analyze: EC2 queries common (15 times)         │
    │     ↓                                               │
    │  5. Improve: Generate more EC2 prompts             │
    │     ↓                                               │
    │  6. Optimize: Cache EC2 query patterns            │
    │     ↓                                               │
    │  7. Next EC2 query: 2.1s (2x faster!) ────────────┘
    │                                                     
    └─────────────────────────────────────────────────────┘
```

## Project 1: The Architecture Inferencer ("The Pivot" of IaC Review)

**Concept:** Instead of reviewing Infrastructure-as-Code (which we don't have access to), we "reverse engineer" the architecture by analyzing billing patterns in the CUR.

### How it works:
1.  **SQL Extraction (`athena_architecture_inference.sql`)**: We run targeted queries to find expensive patterns like:
    *   High Cross-AZ Data Transfer (implies chatty microservices).
    *   High NAT Gateway usage vs S3/DynamoDB usage (implies missing VPC Endpoints).
    *   Legacy volume types (GP2 vs GP3).
2.  **GenAI Analysis**: The Agent receives this data and infers the architecture.
    *   *Input:* "Region A-to-B transfer is 50TB."
    *   *Output:* "You likely have a cluster spanning AZs without local routing. Recommend `use1-az1` preference or Local Zones."

## Project 2: Tagging "Sherlock Holmes" (The Gap Filler)

**Concept:** Since we can't see CloudTrail logs to know *who* created a resource, we use "Time-Travel Correlation" to guess ownership.

### How it works:
1.  **SQL Extraction (`athena_tagging_correlation.sql`)**:
    *   Finds untagged resources.
    *   Finds *other* resources that started billing at the **exact same hour**.
2.  **GenAI Analysis**: The Agent calculates the probability of ownership.
    *   *Input:* "Untagged Volume X started at 10:00 AM. At 10:00 AM, Project 'Payments' launched 5 instances."
    *   *Output:* "95% Confidence Volume X belongs to Project 'Payments'."

## Repository Structure

```
finops-genai-agent/
├── streamlit_app.py              # Main Streamlit application
├── intelligent_agent.py          # Smart AWS service detection agent
├── enhanced_agent.py             # Production agent with DuckDB
├── analytics_dashboard.py        # Usage analytics dashboard
├── requirements.txt              # Python dependencies
├── start.sh / start.bat          # Quick start scripts
├── Dockerfile                    # Container deployment
├── docker-compose.yml            # Docker orchestration
├── sql/                          # SQL query templates
│   ├── athena_architecture_inference.sql
│   └── athena_tagging_correlation.sql
├── scripts/                      # Utility scripts
│   ├── setup_aws.py             # AWS infrastructure setup
│   ├── setup.sh / setup.bat     # Environment setup
│   └── generate_sample_data.py  # Test data generator
├── sample_data/                  # Sample CSV files for testing
├── docs/                         # Documentation
│   ├── QUICKSTART.md
│   ├── RUN_LOCALLY.md
│   ├── TROUBLESHOOTING.md
│   ├── ENHANCEMENTS.md
│   └── ... (more docs)
└── .github/workflows/            # CI/CD pipelines
```

## How to Run the Prototype

### Option 1: Command Line Prototype

```bash
python3 genai_agent_logic.py
```

This will run a simulation showing how the SQL data is fed into an LLM prompt to generate insights.

### Option 2: Interactive Streamlit App (Recommended)

We've built a full-featured Streamlit application with:
- 🧠 **Intelligent Agent** - Works with ANY AWS service SQL output
- 🔍 **Auto-Detection** - Automatically identifies AWS service from your data
- 💡 **Smart Questions** - Generates contextual questions based on your data
- 📁 CSV upload for Athena query results
- 💬 Interactive chat interface powered by AWS Bedrock (Claude 3)
- 📊 Auto-generated visualizations and insights
- 📈 Automatic data profiling and summary tables
- 🎯 Learning capabilities that improve over time

**Quick Start:**

```bash
# Option 1: Use startup script (easiest)
./start.sh              # macOS/Linux
start.bat               # Windows

# Option 2: Manual start
source venv/bin/activate
streamlit run streamlit_app.py
```

**First Time Setup:**

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure AWS credentials
cp .env.example .env
# Edit .env with your AWS credentials

# 5. Setup AWS infrastructure
python scripts/setup_aws.py

# 6. Run the app
streamlit run streamlit_app.py
```

**See [docs/RUN_LOCALLY.md](docs/RUN_LOCALLY.md) for detailed instructions.**

**Documentation:**
- [Quick Start Guide](docs/QUICKSTART.md) - Get running in 5 minutes
- [Run Locally Guide](docs/RUN_LOCALLY.md) - Detailed local setup
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [Full Documentation](docs/README_STREAMLIT.md) - Complete feature guide
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment options
- [Enhancements](docs/ENHANCEMENTS.md) - New features and improvements

**Generate Sample Data (for testing):**

```bash
python scripts/generate_sample_data.py
```

This creates sample CSV files in `sample_data/` that you can upload to test the app without running actual Athena queries.
