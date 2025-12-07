# FinOps GenAI Agent - Streamlit Application

An intelligent Streamlit application that analyzes AWS Cost & Usage Report (CUR) data using GenAI, providing interactive chat-based insights, visualizations, and cost optimization recommendations.

## 🌟 Features

- **📁 CSV Upload**: Upload Athena SQL query results directly
- **💬 Interactive Chat**: Natural language interface powered by AWS Bedrock (Claude 3)
- **💡 Smart Suggestions**: Context-aware prompt suggestions based on your data
- **📊 Auto Visualizations**: Dynamic charts and graphs for cost analysis
- **🧠 Learning Agent**: Stores interactions in DynamoDB to improve over time
- **🎯 Multi-Analysis Modes**:
  - Architecture Inference (detect inefficiencies)
  - Tagging Analysis (find untagged resources)
  - General Cost Analysis

## 🏗️ Architecture

```
User → Streamlit UI → AWS Bedrock (Claude 3) → Insights
                   ↓
              DynamoDB (Learning Storage)
```

### AWS Services Used

1. **AWS Bedrock**: Claude 3 Sonnet for intelligent analysis
2. **Amazon DynamoDB**: Store user interactions for continuous learning
3. **Amazon Athena**: (External) Query CUR data
4. **Amazon S3**: (External) Store CUR data

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- AWS Account with:
  - Bedrock enabled (Claude 3 model access)
  - DynamoDB access
  - Athena access (for running SQL queries)
- AWS CLI configured with credentials

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/bgandhi001/finops-genai-agent.git
cd finops-genai-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure AWS credentials**
```bash
aws configure
# OR copy .env.example to .env and fill in your credentials
cp .env.example .env
```

4. **Setup AWS infrastructure**
```bash
python setup_aws.py
```

This will:
- Create DynamoDB table for learning storage
- Verify Bedrock access
- Display required IAM policies

5. **Enable Bedrock Model Access**
- Go to AWS Console → Bedrock → Model Access
- Request access to "Anthropic Claude 3 Sonnet"
- Wait for approval (usually instant)

### Running the Application

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Step 1: Run Athena Queries

Use the provided SQL queries to extract data from your CUR:

**For Architecture Analysis:**
```sql
-- Use queries from athena_architecture_inference.sql
-- Export results as CSV
```

**For Tagging Analysis:**
```sql
-- Use queries from athena_tagging_correlation.sql
-- Export results as CSV
```

### Step 2: Upload Data

1. Open the Streamlit app
2. Select analysis type in sidebar
3. Upload your CSV file from Athena
4. View data preview and summary

### Step 3: Interact with Agent

**Option A: Use Suggested Prompts**
- Click any suggested question button
- Agent analyzes and responds with insights

**Option B: Custom Questions**
- Type your question in the chat input
- Examples:
  - "What are the top 3 cost optimization opportunities?"
  - "Show me a breakdown by availability zone"
  - "Calculate potential savings from VPC endpoints"

### Step 4: Review Insights

- Read AI-generated recommendations
- View auto-generated visualizations
- Export findings for your team

## 🎯 Example Queries

### Architecture Inference
- "Analyze cross-AZ data transfer patterns"
- "Identify missing VPC endpoints"
- "Find legacy GP2 volumes that should be GP3"
- "Calculate potential savings from architectural changes"

### Tagging Analysis
- "Find untagged resources and suggest owners"
- "Show correlation between resources created at the same time"
- "What's the confidence score for tag recommendations?"
- "Generate a tagging remediation plan"

### General Analysis
- "Summarize key cost drivers"
- "Show me cost trends over time"
- "Create a prioritized action plan"
- "What are the quick wins?"

## 🧠 Learning Capabilities

The agent learns from interactions by:

1. **Storing Queries**: All user questions saved to DynamoDB
2. **Context Awareness**: Uses previous conversation for better responses
3. **Pattern Recognition**: Identifies common questions and optimizes responses
4. **Feedback Loop**: Improves recommendations based on usage patterns

### DynamoDB Schema

```python
{
  'interaction_id': 'timestamp',
  'timestamp': 'ISO-8601',
  'user_query': 'string',
  'agent_response': 'string',
  'data_context': 'json',
  'session_id': 'string'
}
```

## 🔧 Configuration

### Environment Variables

```bash
AWS_REGION=us-east-1
DYNAMODB_TABLE=finops-agent-interactions
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### Customization

**Change Bedrock Model:**
Edit `streamlit_app.py`:
```python
modelId='anthropic.claude-3-sonnet-20240229-v1:0'  # Change this
```

**Adjust Chat History:**
```python
for msg in chat_history[-5:]  # Change number of messages
```

## 📊 Visualization Types

The app automatically generates:

1. **Bar Charts**: Top cost drivers
2. **Pie Charts**: Cost distribution
3. **Time Series**: Cost trends (if date columns present)
4. **Heatmaps**: Resource correlation matrices

## 🔒 Security Best Practices

1. **Never commit credentials**: Use `.env` file (gitignored)
2. **Use IAM roles**: Prefer roles over access keys in production
3. **Least privilege**: Apply minimal IAM permissions
4. **Encrypt data**: DynamoDB encryption at rest enabled by default
5. **VPC deployment**: Run in private subnet for production

## 💰 Cost Estimation

Typical monthly costs for moderate usage:

- **Bedrock (Claude 3 Sonnet)**: ~$10-50 (pay per token)
- **DynamoDB**: ~$1-5 (pay per request)
- **Athena**: ~$5 per TB scanned
- **S3**: Minimal (CUR storage)

**Total**: ~$15-60/month

## 🐛 Troubleshooting

### "Error calling Bedrock"
- Verify Bedrock is enabled in your region
- Check model access is granted
- Confirm IAM permissions

### "Could not save interaction"
- Verify DynamoDB table exists
- Check table name matches configuration
- Confirm IAM permissions for DynamoDB

### "No data to display"
- Ensure CSV has required columns (cost, resource info)
- Check CSV format matches Athena output
- Verify file upload completed

## 🚀 Deployment Options

### Option 1: Local Development
```bash
streamlit run streamlit_app.py
```

### Option 2: AWS EC2
```bash
# Install on EC2 instance
# Use IAM role for credentials
# Run with systemd service
```

### Option 3: AWS ECS/Fargate
```dockerfile
# Use provided Dockerfile
# Deploy as container
# Use task role for AWS access
```

### Option 4: Streamlit Cloud
- Connect GitHub repo
- Add secrets in Streamlit Cloud dashboard
- Deploy with one click

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues or questions:
- Open a GitHub issue
- Check existing documentation
- Review AWS Bedrock documentation

## 🎓 Learn More

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [AWS Cost & Usage Report](https://docs.aws.amazon.com/cur/)
- [FinOps Foundation](https://www.finops.org/)
