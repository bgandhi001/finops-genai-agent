# 🚀 Quick Start Guide - FinOps GenAI Agent

Get up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- AWS Account
- AWS CLI configured

## Step 1: Clone & Install (2 min)

```bash
git clone https://github.com/bgandhi001/finops-genai-agent.git
cd finops-genai-agent
pip install -r requirements.txt
```

## Step 2: Configure AWS (1 min)

```bash
# Option A: Use AWS CLI
aws configure

# Option B: Use environment file
cp .env.example .env
# Edit .env with your credentials
```

## Step 3: Setup Infrastructure (1 min)

```bash
python setup_aws.py
```

This creates:
- DynamoDB table for learning
- Verifies Bedrock access

## Step 4: Enable Bedrock Model (1 min)

1. Go to AWS Console → Bedrock → Model Access
2. Click "Manage model access"
3. Enable "Anthropic Claude 3 Sonnet"
4. Click "Save changes"

## Step 5: Run the App! (30 sec)

```bash
streamlit run streamlit_app.py
```

Opens at: http://localhost:8501

## Step 6: Try It Out

1. **Run Athena Query**
   - Copy SQL from `athena_architecture_inference.sql`
   - Run in AWS Athena Console
   - Download results as CSV

2. **Upload to App**
   - Click "Browse files" in sidebar
   - Upload your CSV
   - Select analysis type

3. **Ask Questions**
   - Click suggested prompts, or
   - Type your own questions
   - Get AI-powered insights!

## Example Workflow

```bash
# 1. Query your CUR data in Athena
SELECT line_item_product_code, 
       SUM(line_item_unblended_cost) as total_cost
FROM cost_and_usage_report
WHERE line_item_usage_start_date >= DATE_ADD('day', -30, CURRENT_DATE)
GROUP BY line_item_product_code
ORDER BY total_cost DESC;

# 2. Download CSV

# 3. Upload to Streamlit app

# 4. Ask: "What are my top 3 cost optimization opportunities?"

# 5. Get actionable insights with charts!
```

## Troubleshooting

**"Error calling Bedrock"**
- Enable Claude 3 model access in AWS Console
- Check IAM permissions

**"Could not save interaction"**
- Run `python setup_aws.py` again
- Verify DynamoDB permissions

**"No module named 'streamlit'"**
- Run `pip install -r requirements.txt`

## Next Steps

- Read [README_STREAMLIT.md](README_STREAMLIT.md) for full features
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Explore example SQL queries in repo

## Need Help?

- Open a GitHub issue
- Check AWS Bedrock documentation
- Review CloudWatch logs

---

**That's it! You're ready to optimize your AWS costs with AI! 🎉**
