# Troubleshooting Guide

## Common Issues and Solutions

### 1. JSON Serialization Error

**Error:**
```
Error calling Bedrock: Object of type Timestamp is not JSON serializable
```

**Cause:** DuckDB returns Timestamp objects that can't be directly serialized to JSON.

**Solution:** ✅ Fixed in latest version
- The app now automatically converts Timestamp objects to ISO format strings
- Update to latest version: `git pull origin main`

---

### 2. Module Not Found Errors

#### "ModuleNotFoundError: No module named 'duckdb'"

**Solution:**
```bash
source venv/bin/activate
pip install duckdb
```

#### "ModuleNotFoundError: No module named 'streamlit'"

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

### 3. AWS Credentials Issues

#### "Unable to locate credentials"

**Solution:**
```bash
# Option 1: Edit .env file
nano .env
# Add your AWS credentials

# Option 2: Set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

#### "Error calling Bedrock: Access Denied"

**Solutions:**
1. Enable Bedrock model access in AWS Console
2. Check IAM permissions include `bedrock:InvokeModel`
3. Verify region supports Bedrock (us-east-1, us-west-2, etc.)

---

### 4. Virtual Environment Issues

#### "command not found: streamlit"

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # You should see (venv) in prompt

# If still not working, reinstall
pip install streamlit
```

#### Virtual environment not activating

**Solution:**
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 5. File Upload Issues

#### "Failed to load data"

**Solutions:**
1. Check CSV file is valid
2. Ensure file has headers
3. Try with smaller file first
4. Check file encoding (should be UTF-8)

#### "Memory Error" with large files

**Solution:** ✅ Should not happen with EnhancedAgent
- Ensure you're using latest version
- EnhancedAgent handles 10GB+ files
- If still occurring, check available disk space

---

### 6. Bedrock Issues

#### "Model not found"

**Solution:**
1. Go to AWS Console → Bedrock → Model Access
2. Enable "Anthropic Claude 3 Sonnet"
3. Wait for approval (usually instant)

#### "Rate limit exceeded"

**Solution:**
1. Wait a few seconds between requests
2. Request quota increase in AWS Console
3. Implement request throttling

---

### 7. DynamoDB Issues

#### "Table does not exist"

**Solution:**
```bash
python setup_aws.py
```

#### "Access Denied" to DynamoDB

**Solution:**
Check IAM permissions include:
```json
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:PutItem",
    "dynamodb:GetItem",
    "dynamodb:Query"
  ],
  "Resource": "arn:aws:dynamodb:*:*:table/finops-agent-interactions"
}
```

---

### 8. SQL Execution Errors

#### "SQL Error: Dangerous operation not allowed"

**Cause:** Trying to use DROP, DELETE, or other dangerous SQL operations

**Solution:** Only SELECT queries are allowed for security
```sql
-- ✅ Allowed
SELECT * FROM aws_data LIMIT 10

-- ❌ Not allowed
DROP TABLE aws_data
DELETE FROM aws_data
```

#### "SQL Error: Column not found"

**Solution:**
1. Check column names in data preview
2. Column names are case-sensitive
3. Use exact column names from your CSV

---

### 9. Performance Issues

#### App is slow

**Solutions:**
1. Ensure using EnhancedAgent (check latest version)
2. Clear Streamlit cache: `streamlit cache clear`
3. Restart the app
4. Check system resources (CPU, RAM)

#### Visualizations not loading

**Solutions:**
1. Check data has numeric columns
2. Ensure cost columns exist
3. Try with smaller dataset first
4. Check browser console for errors

---

### 10. Port Already in Use

**Error:**
```
Port 8501 is already in use
```

**Solutions:**
```bash
# Option 1: Kill existing process
lsof -ti:8501 | xargs kill -9

# Option 2: Use different port
streamlit run streamlit_app.py --server.port 8502
```

---

## Debugging Tips

### Enable Debug Logging

```bash
streamlit run streamlit_app.py --logger.level=debug
```

### Check Python Version

```bash
python --version
# Should be 3.8 or higher
```

### Verify Dependencies

```bash
pip list | grep -E "(streamlit|duckdb|boto3|plotly|pandas)"
```

### Test AWS Connection

```bash
python -c "import boto3; print(boto3.client('sts').get_caller_identity())"
```

### Clear All Caches

```bash
streamlit cache clear
rm -rf ~/.streamlit/cache
```

---

## Getting More Help

### Check Documentation

- [RUN_LOCALLY.md](RUN_LOCALLY.md) - Local setup
- [GET_AWS_CREDENTIALS.md](GET_AWS_CREDENTIALS.md) - AWS credentials
- [VIRTUAL_ENV_GUIDE.md](VIRTUAL_ENV_GUIDE.md) - Virtual environment
- [ENHANCEMENTS.md](ENHANCEMENTS.md) - New features
- [AGENT_COMPARISON.md](AGENT_COMPARISON.md) - Agent differences

### Still Having Issues?

1. Check GitHub Issues: https://github.com/bgandhi001/finops-genai-agent/issues
2. Review error messages carefully
3. Check AWS CloudWatch logs
4. Verify all prerequisites are met
5. Try with sample data first

---

## Quick Fixes Checklist

- [ ] Virtual environment activated (`source venv/bin/activate`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] AWS credentials configured (`.env` file or environment variables)
- [ ] Bedrock model access enabled
- [ ] DynamoDB table created (`python setup_aws.py`)
- [ ] Using latest code (`git pull origin main`)
- [ ] Python 3.8+ installed
- [ ] Sufficient disk space available
- [ ] Network connectivity to AWS

---

**Most issues can be resolved by ensuring virtual environment is activated and dependencies are installed!** 🔧
