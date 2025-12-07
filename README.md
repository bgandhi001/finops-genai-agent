# FinOps GenAI Agent Project

This repository contains the blueprints for two "Cool GenAI Projects" for a FinOps Architect, specifically tailored for scenarios where you **only have access to the Cost & Usage Report (CUR)** (via Athena) and not the customer's actual AWS account APIs.

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

## Files in this Repo

*   **`athena_architecture_inference.sql`**: SQL queries to detect architectural cost anomalies.
*   **`athena_tagging_correlation.sql`**: SQL queries to correlate untagged resources with tagged ones.
*   **`genai_agent_logic.py`**: A Python prototype demonstrating how an Agent constructs prompts from the SQL data and interprets the results.

## How to Run the Prototype

### Option 1: Command Line Prototype

```bash
python3 genai_agent_logic.py
```

This will run a simulation showing how the SQL data is fed into an LLM prompt to generate insights.

### Option 2: Interactive Streamlit App (Recommended)

We've built a full-featured Streamlit application with:
- 📁 CSV upload for Athena query results
- 💬 Interactive chat interface powered by AWS Bedrock (Claude 3)
- 📊 Auto-generated visualizations and insights
- 🧠 Learning capabilities that improve over time
- 💡 Smart prompt suggestions based on your data

**Quick Start:**

```bash
# Install dependencies
pip install -r requirements.txt

# Setup AWS infrastructure
python setup_aws.py

# Run the app
streamlit run streamlit_app.py
```

**Documentation:**
- [Quick Start Guide](QUICKSTART.md) - Get running in 5 minutes
- [Full Documentation](README_STREAMLIT.md) - Complete feature guide
- [Deployment Guide](DEPLOYMENT.md) - Production deployment options

**Generate Sample Data (for testing):**

```bash
python generate_sample_data.py
```

This creates sample CSV files you can upload to test the app without running actual Athena queries.
