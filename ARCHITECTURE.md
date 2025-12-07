# Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ File Upload  │  │ Chat Input   │  │ Visualizations│        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Application                        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Application Logic Layer                      │ │
│  │                                                            │ │
│  │  • Data Processing (Pandas)                               │ │
│  │  • Session Management                                     │ │
│  │  • Context Building                                       │ │
│  │  • Prompt Engineering                                     │ │
│  │  • Response Formatting                                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
                             │
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│              │    │              │    │              │
│ AWS Bedrock  │    │  DynamoDB    │    │   Athena     │
│  (Claude 3)  │    │              │    │              │
│              │    │              │    │              │
│ • Analysis   │    │ • Learning   │    │ • CUR Data   │
│ • Insights   │    │ • History    │    │ • Queries    │
│ • Recommendations│ │ • Patterns   │    │ • Results    │
│              │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Data Flow

### 1. Upload & Analysis Flow

```
User Uploads CSV
      │
      ▼
Parse & Validate Data
      │
      ▼
Generate Data Summary
      │
      ▼
Create Suggested Prompts
      │
      ▼
Display UI with Context
```

### 2. Query Processing Flow

```
User Enters Query
      │
      ▼
Build Context
  • Current data summary
  • Sample data rows
  • Chat history (last 5)
  • Analysis type
      │
      ▼
Construct Prompt
  • System instructions
  • Context data (JSON)
  • Conversation history
  • User query
      │
      ▼
Call AWS Bedrock
  • Model: Claude 3 Sonnet
  • Max tokens: 4096
  • Temperature: 0.7
      │
      ▼
Process Response
  • Parse markdown
  • Extract insights
  • Generate visualizations
      │
      ▼
Save to DynamoDB
  • Query
  • Response
  • Context
  • Timestamp
      │
      ▼
Display to User
```

### 3. Visualization Flow

```
Detect Visualization Request
      │
      ▼
Identify Data Columns
  • Cost columns
  • Grouping columns
  • Date columns
      │
      ▼
Select Chart Type
  • Bar chart (top N)
  • Pie chart (distribution)
  • Time series (trends)
      │
      ▼
Generate with Plotly
      │
      ▼
Render in UI
```

## Component Details

### Frontend Components

#### 1. Sidebar
```python
- Analysis Type Selector
- File Upload Widget
- Data Preview Expander
- AWS Configuration
- Session Info
```

#### 2. Main Area
```python
- Metrics Row (4 columns)
  • Total Rows
  • Total Cost
  • Columns
  • Analysis Type

- Suggested Prompts (5 buttons)

- Chat Interface
  • Message History
  • User Input
  • Agent Responses
  • Inline Charts

- Visualization Section
  • Bar Chart
  • Pie Chart
```

### Backend Components

#### 1. Data Processing
```python
def analyze_uploaded_data(df):
    """
    Extract metadata from uploaded CSV
    - Row/column counts
    - Detect cost columns
    - Identify numeric columns
    - Calculate totals
    """
```

#### 2. Prompt Engineering
```python
def call_bedrock_llm(prompt, context, history):
    """
    Build comprehensive prompt with:
    - System role definition
    - Context data (JSON)
    - Conversation history
    - User query
    - Output format instructions
    """
```

#### 3. Learning System
```python
def save_interaction_to_dynamodb(query, response, context):
    """
    Store interaction for learning:
    - Interaction ID (timestamp)
    - User query
    - Agent response
    - Data context
    - Session ID
    """
```

## AWS Service Integration

### 1. AWS Bedrock

**Purpose**: LLM inference for intelligent analysis

**Configuration**:
```python
client = boto3.client('bedrock-runtime', region_name='us-east-1')
model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
```

**Request Format**:
```json
{
  "anthropic_version": "bedrock-2023-05-31",
  "max_tokens": 4096,
  "messages": [
    {
      "role": "user",
      "content": "<prompt>"
    }
  ],
  "temperature": 0.7
}
```

**Response Format**:
```json
{
  "content": [
    {
      "text": "<response>"
    }
  ]
}
```

### 2. Amazon DynamoDB

**Purpose**: Store user interactions for learning

**Table Schema**:
```
Table: finops-agent-interactions
Partition Key: interaction_id (String)

Attributes:
- interaction_id: timestamp
- timestamp: ISO-8601 string
- user_query: string
- agent_response: string
- data_context: JSON string
- session_id: string
```

**Access Pattern**:
```python
# Write
table.put_item(Item={...})

# Read (future)
table.query(
    KeyConditionExpression=Key('session_id').eq(session_id)
)
```

### 3. Amazon Athena

**Purpose**: Query CUR data (external to app)

**Integration**:
- User runs SQL queries in Athena Console
- Downloads results as CSV
- Uploads CSV to Streamlit app

**Query Types**:
1. Architecture Inference
2. Tagging Correlation
3. Cost Analysis

## Security Architecture

### 1. Authentication & Authorization

```
User → Streamlit App → AWS IAM Role → AWS Services
                          │
                          ├─ Bedrock (InvokeModel)
                          ├─ DynamoDB (PutItem, Query)
                          └─ Athena (StartQueryExecution)
```

### 2. Data Protection

**In Transit**:
- HTTPS for all connections
- TLS 1.2+ for AWS API calls

**At Rest**:
- DynamoDB encryption enabled by default
- S3 encryption for Athena results

**In Memory**:
- Session state isolated per user
- No persistent local storage

### 3. IAM Policies

**Minimum Required Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/finops-agent-interactions"
    }
  ]
}
```

## Deployment Architectures

### Option 1: Local Development

```
Developer Machine
├── Python 3.11
├── Streamlit (port 8501)
└── AWS Credentials (CLI)
```

### Option 2: Docker Container

```
Docker Host
└── Container
    ├── Python 3.11
    ├── Streamlit App
    └── Environment Variables
```

### Option 3: AWS ECS/Fargate

```
┌─────────────────────────────────────┐
│          Application Load Balancer   │
│              (Port 443)              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         ECS Service                  │
│                                      │
│  ┌────────────────────────────────┐ │
│  │  Fargate Task                  │ │
│  │  ├── Container (Streamlit)     │ │
│  │  └── Task Role (IAM)           │ │
│  └────────────────────────────────┘ │
│                                      │
│  Desired Count: 1-3                 │
│  Auto Scaling: CPU/Memory based     │
└─────────────────────────────────────┘
```

### Option 4: Streamlit Cloud

```
GitHub Repository
      │
      ▼
Streamlit Cloud
├── Automatic Deployment
├── Secrets Management
└── Built-in Scaling
```

## Performance Optimization

### 1. Caching Strategy

```python
@st.cache_resource
def get_bedrock_client():
    """Cache AWS client across requests"""
    return boto3.client('bedrock-runtime')

@st.cache_data
def analyze_uploaded_data(df):
    """Cache data analysis results"""
    return summary
```

### 2. Response Time Breakdown

```
Total Response Time: 5-10 seconds
├── Data Processing: 0.5s
├── Prompt Building: 0.2s
├── Bedrock API Call: 3-8s
├── Response Parsing: 0.2s
└── Visualization: 0.5s
```

### 3. Scalability Considerations

**Vertical Scaling**:
- Increase Fargate CPU/Memory
- Use larger EC2 instances

**Horizontal Scaling**:
- Multiple ECS tasks behind ALB
- Session affinity not required
- Stateless design

**Database Scaling**:
- DynamoDB auto-scales
- On-demand billing mode
- No capacity planning needed

## Monitoring & Observability

### 1. Application Metrics

```python
# Custom metrics to track
- Queries per session
- Response time per query
- Error rate
- User satisfaction
- Feature usage
```

### 2. AWS CloudWatch

```
Metrics:
├── ECS Task CPU/Memory
├── ALB Request Count
├── Bedrock Invocations
├── DynamoDB Read/Write Units
└── Application Logs
```

### 3. Logging Strategy

```python
# Log levels
INFO: User actions, successful operations
WARNING: Recoverable errors, fallbacks
ERROR: Failed operations, exceptions
DEBUG: Detailed execution flow
```

## Disaster Recovery

### 1. Backup Strategy

**DynamoDB**:
- Point-in-time recovery enabled
- On-demand backups
- Cross-region replication (optional)

**Application**:
- Code in GitHub (version controlled)
- Docker images in ECR
- Infrastructure as Code

### 2. Recovery Procedures

**Application Failure**:
1. ECS auto-restarts failed tasks
2. ALB health checks detect issues
3. Auto-scaling replaces unhealthy tasks

**Data Loss**:
1. Restore DynamoDB from backup
2. Replay interactions if needed
3. No critical data loss (learning only)

## Future Architecture Enhancements

### Phase 1: Multi-tenancy
```
Add user authentication
Isolate data by tenant
Implement RBAC
```

### Phase 2: Microservices
```
Separate services:
├── API Gateway
├── Analysis Service
├── Visualization Service
└── Learning Service
```

### Phase 3: Real-time Processing
```
Add streaming:
├── Kinesis Data Streams
├── Lambda processors
└── Real-time dashboards
```

### Phase 4: Multi-cloud
```
Support:
├── AWS (current)
├── Azure
└── GCP
```

---

**Architecture Version**: 1.0  
**Last Updated**: December 2024  
**Status**: Production Ready
