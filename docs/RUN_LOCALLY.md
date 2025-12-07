# How to Run FinOps GenAI Agent Locally

## Quick Start (5 Minutes)

### Step 1: Activate Virtual Environment

```bash
# Navigate to project directory
cd finops-genai-agent

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

You should see `(venv)` in your terminal prompt.

### Step 2: Install/Update Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

This installs:
- streamlit
- pandas
- boto3
- plotly
- duckdb (new!)

### Step 3: Configure AWS Credentials

**Option A: Using .env file (Easiest)**

```bash
# Edit the .env file
nano .env  # or use any text editor
```

Add your AWS credentials:
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...your_key_here
AWS_SECRET_ACCESS_KEY=wJal...your_secret_here
DYNAMODB_TABLE=finops-agent-interactions
```

**Option B: Using Environment Variables**

```bash
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_here
```

### Step 4: Setup AWS Infrastructure (First Time Only)

```bash
python setup_aws.py
```

This creates the DynamoDB table for logging.

### Step 5: Run the App!

```bash
streamlit run streamlit_app.py
```

The app will open automatically in your browser at: **http://localhost:8501**

---

## Detailed Instructions

### Prerequisites Check

Before starting, verify you have:

```bash
# Check Python version (need 3.8+)
python --version

# Check if virtual environment exists
ls venv/

# Check if .env file exists
ls .env
```

### If Virtual Environment Doesn't Exist

```bash
# Create new virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### If You Don't Have AWS Credentials

1. **Go to AWS Console**: https://console.aws.amazon.com/
2. **Navigate to IAM** → Users → Add users
3. **Create user** with programmatic access
4. **Attach policies**:
   - AmazonBedrockFullAccess
   - AmazonDynamoDBFullAccess
5. **Download credentials** (CSV file)
6. **Add to .env file**

See [GET_AWS_CREDENTIALS.md](GET_AWS_CREDENTIALS.md) for detailed instructions.

### Enable AWS Bedrock

1. Go to **AWS Console** → **Bedrock** → **Model Access**
2. Click **"Manage model access"**
3. Enable **"Anthropic Claude 3 Sonnet"**
4. Click **"Save changes"**

---

## Running Different Components

### Main Application

```bash
streamlit run streamlit_app.py
```

### Analytics Dashboard

```bash
streamlit run analytics_dashboard.py
```

### Generate Sample Data (for testing)

```bash
python generate_sample_data.py
```

This creates test CSV files you can upload without needing real AWS data.

---

## Troubleshooting

### "streamlit: command not found"

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall streamlit
pip install streamlit
```

### "ModuleNotFoundError: No module named 'duckdb'"

**Solution:**
```bash
pip install duckdb
```

### "Unable to locate credentials"

**Solution:**
```bash
# Check .env file exists and has credentials
cat .env

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

### "Error calling Bedrock"

**Solutions:**
1. Enable Bedrock model access in AWS Console
2. Check IAM permissions
3. Verify AWS region supports Bedrock (us-east-1, us-west-2)

### Port Already in Use

**Solution:**
```bash
# Run on different port
streamlit run streamlit_app.py --server.port 8502
```

### App Won't Start

**Solution:**
```bash
# Check for errors
streamlit run streamlit_app.py --logger.level=debug

# Clear cache
streamlit cache clear
```

---

## Testing Without AWS

You can test the app without AWS credentials:

### Step 1: Generate Sample Data

```bash
python generate_sample_data.py
```

### Step 2: Comment Out AWS Calls

In `streamlit_app.py`, temporarily disable AWS calls:

```python
# Comment out Bedrock calls for testing
# response = call_bedrock_llm(...)
response = "This is a test response"
```

### Step 3: Run App

```bash
streamlit run streamlit_app.py
```

Upload the generated sample CSV files to test the UI.

---

## Development Mode

### Auto-Reload on Changes

Streamlit automatically reloads when you save files. Just edit and save!

### View Logs

```bash
# Run with debug logging
streamlit run streamlit_app.py --logger.level=debug
```

### Clear Cache

```bash
# Clear all cached data
streamlit cache clear
```

---

## Stopping the App

### In Terminal

Press `Ctrl+C` to stop the Streamlit server.

### Deactivate Virtual Environment

```bash
deactivate
```

---

## Common Workflows

### Daily Development

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Run app
streamlit run streamlit_app.py

# 3. Make changes (app auto-reloads)

# 4. Stop with Ctrl+C when done

# 5. Deactivate
deactivate
```

### Testing New Features

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Generate test data
python generate_sample_data.py

# 3. Run app
streamlit run streamlit_app.py

# 4. Upload sample CSV files

# 5. Test features
```

### Updating Dependencies

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Update packages
pip install --upgrade -r requirements.txt

# 3. Test app
streamlit run streamlit_app.py
```

---

## Environment Variables Reference

### Required

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

### Optional

```bash
DYNAMODB_TABLE=finops-agent-interactions
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

---

## File Structure

```
finops-genai-agent/
├── venv/                          # Virtual environment
├── .env                           # AWS credentials (DO NOT COMMIT)
├── streamlit_app.py              # Main application
├── intelligent_agent.py          # Original agent
├── enhanced_agent.py             # Enhanced agent with DuckDB
├── analytics_dashboard.py        # Analytics viewer
├── setup_aws.py                  # AWS setup script
├── generate_sample_data.py       # Test data generator
├── requirements.txt              # Python dependencies
└── *.md                          # Documentation
```

---

## Quick Commands Reference

```bash
# Activate environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup AWS
python setup_aws.py

# Run main app
streamlit run streamlit_app.py

# Run analytics
streamlit run analytics_dashboard.py

# Generate test data
python generate_sample_data.py

# Stop app
Ctrl+C

# Deactivate environment
deactivate
```

---

## Next Steps

1. ✅ Run the app locally
2. ✅ Upload a CSV file
3. ✅ Try the smart questions
4. ✅ Ask custom questions
5. ✅ View visualizations
6. ✅ Check analytics dashboard

---

## Getting Help

- **Documentation**: Check the README files
- **Credentials**: See [GET_AWS_CREDENTIALS.md](GET_AWS_CREDENTIALS.md)
- **Virtual Env**: See [VIRTUAL_ENV_GUIDE.md](VIRTUAL_ENV_GUIDE.md)
- **AWS Setup**: See [AWS_CLI_SETUP.md](AWS_CLI_SETUP.md)
- **Issues**: Open a GitHub issue

---

**You're ready to run the FinOps GenAI Agent locally!** 🚀
