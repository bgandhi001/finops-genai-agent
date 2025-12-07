# Learning System Documentation

## Overview

The FinOps GenAI Agent includes a comprehensive learning system that captures user interactions, analyzes patterns, and improves over time. All data is stored in Amazon DynamoDB for analysis and continuous improvement.

## How Learning Works

### 1. Data Collection

The agent automatically logs:
- ✅ **Session Events** - Start, end, duration
- ✅ **File Uploads** - Metadata (not content)
- ✅ **User Queries** - Questions asked
- ✅ **Agent Responses** - Answers provided
- ✅ **Performance Metrics** - Response times, success rates
- ✅ **Usage Patterns** - Feature usage, query types

### 2. Storage Architecture

**Technology:** Amazon DynamoDB
**Table:** `finops-agent-interactions`
**Retention:** 90 days (automatic TTL)
**Encryption:** At rest (default)

### 3. Privacy & Security

**What We Store:**
- ✅ Session metadata
- ✅ Query text
- ✅ Response summaries (truncated)
- ✅ Performance metrics
- ✅ Usage statistics

**What We DON'T Store:**
- ❌ Actual file content
- ❌ Sensitive data values
- ❌ Personal information
- ❌ AWS credentials
- ❌ Full response text (only first 1000 chars)

## Learning Capabilities

### 1. Session Tracking

**What's Tracked:**
```python
{
    'session_id': 'unique-uuid',
    'session_start': '2024-12-07T10:00:00Z',
    'session_duration': 1800,  # seconds
    'total_queries': 5,
    'total_uploads': 1,
    'chat_messages': 10
}
```

**Use Cases:**
- Understand user engagement
- Identify session patterns
- Optimize user experience
- Track feature adoption

### 2. Query Pattern Analysis

**What's Tracked:**
```python
{
    'user_query': 'What are my top cost drivers?',
    'query_length': 28,
    'is_suggested_prompt': False,
    'analysis_type': 'Cost Analysis',
    'has_data': True
}
```

**Learning Outcomes:**
- Most common questions
- Suggested vs custom queries
- Query complexity patterns
- Popular analysis types

### 3. Response Quality Metrics

**What's Tracked:**
```python
{
    'processing_time': 4.5,  # seconds
    'response_length': 1500,
    'has_visualization': True,
    'analysis_type': 'EC2',
    'data_summary': {...}
}
```

**Learning Outcomes:**
- Response time optimization
- Visualization effectiveness
- Service-specific patterns
- Performance bottlenecks

### 4. File Upload Patterns

**What's Tracked:**
```python
{
    'file_name': 'cost_data.csv',
    'file_size': 1024000,
    'row_count': 500,
    'column_count': 10,
    'analysis_type': 'EC2'
}
```

**Learning Outcomes:**
- Common data structures
- File size patterns
- Service distribution
- Data quality issues

## How the Agent Learns

### 1. Pattern Recognition

**Query Clustering:**
- Groups similar questions
- Identifies common themes
- Suggests better prompts
- Improves question generation

**Example:**
```
Queries about "cost" → Generate more cost-related prompts
Queries about "EC2" → Improve EC2-specific analysis
```

### 2. Response Optimization

**Performance Tuning:**
- Identifies slow queries
- Optimizes SQL generation
- Caches common results
- Improves prompt engineering

**Example:**
```
If "top 10 costs" takes 5s → Optimize SQL query
If visualization fails → Improve chart generation
```

### 3. Context Awareness

**Conversation History:**
- Maintains last 5 messages
- Understands context
- Provides relevant follow-ups
- Improves coherence

**Example:**
```
User: "Show me EC2 costs"
Agent: [Shows EC2 costs]
User: "What about S3?"
Agent: [Understands context, shows S3 costs]
```

### 4. Continuous Improvement

**Feedback Loop:**
```
User Query → Agent Response → Log Interaction → Analyze Patterns → Improve Prompts
```

## Analytics Dashboard

### Viewing Learning Data

```bash
streamlit run analytics_dashboard.py
```

**Available Metrics:**
- Total sessions
- Total queries
- Average response time
- Query patterns
- Service distribution
- Usage trends

### Key Insights

1. **Most Popular Questions**
   - What users ask most
   - Suggested vs custom
   - Success rates

2. **Performance Metrics**
   - Response times
   - Processing duration
   - Error rates

3. **Usage Patterns**
   - Peak usage times
   - Session duration
   - Feature adoption

4. **Service Distribution**
   - Which AWS services analyzed
   - Query types per service
   - Cost patterns

## DynamoDB Schema

### Event Types

#### 1. Session Start
```json
{
  "interaction_id": "session_abc123",
  "timestamp": "2024-12-07T10:00:00Z",
  "event_type": "session_start",
  "session_id": "abc123",
  "session_start": "2024-12-07T10:00:00Z",
  "user_agent": "streamlit_app",
  "ttl": 1234567890
}
```

#### 2. File Upload
```json
{
  "interaction_id": "upload_abc123_1",
  "timestamp": "2024-12-07T10:01:00Z",
  "event_type": "file_upload",
  "session_id": "abc123",
  "file_name": "cost_data.csv",
  "file_size": 1024000,
  "row_count": 500,
  "column_count": 10,
  "analysis_type": "EC2",
  "ttl": 1234567890
}
```

#### 3. User Query
```json
{
  "interaction_id": "query_abc123_1",
  "timestamp": "2024-12-07T10:02:00Z",
  "event_type": "user_query",
  "session_id": "abc123",
  "user_query": "What are my top cost drivers?",
  "query_length": 28,
  "is_suggested_prompt": false,
  "analysis_type": "Cost Analysis",
  "has_data": true,
  "ttl": 1234567890
}
```

#### 4. Agent Response
```json
{
  "interaction_id": "response_abc123_1",
  "timestamp": "2024-12-07T10:02:05Z",
  "event_type": "agent_response",
  "session_id": "abc123",
  "user_query": "What are my top cost drivers?",
  "agent_response": "Based on your data...",
  "response_length": 1500,
  "processing_time": 4.5,
  "has_visualization": true,
  "analysis_type": "Cost Analysis",
  "data_summary": "{...}",
  "ttl": 1234567890
}
```

#### 5. Session End
```json
{
  "interaction_id": "session_end_abc123",
  "timestamp": "2024-12-07T10:30:00Z",
  "event_type": "session_end",
  "session_id": "abc123",
  "session_duration": 1800,
  "total_queries": 5,
  "total_uploads": 1,
  "chat_messages": 10,
  "ttl": 1234567890
}
```

## Querying Learning Data

### Using AWS CLI

```bash
# Get all events for a session
aws dynamodb query \
  --table-name finops-agent-interactions \
  --key-condition-expression "session_id = :sid" \
  --expression-attribute-values '{":sid":{"S":"abc123"}}'

# Get recent queries
aws dynamodb scan \
  --table-name finops-agent-interactions \
  --filter-expression "event_type = :type" \
  --expression-attribute-values '{":type":{"S":"user_query"}}'
```

### Using Python

```python
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('finops-agent-interactions')

# Get session data
response = table.query(
    KeyConditionExpression='session_id = :sid',
    ExpressionAttributeValues={':sid': 'abc123'}
)

# Analyze patterns
queries = [item for item in response['Items'] if item['event_type'] == 'user_query']
```

## Machine Learning Potential

### Future Enhancements

1. **Query Prediction**
   - Predict next question
   - Suggest related queries
   - Auto-complete queries

2. **Anomaly Detection**
   - Detect unusual patterns
   - Flag potential issues
   - Alert on anomalies

3. **Personalization**
   - User-specific suggestions
   - Customized prompts
   - Adaptive UI

4. **Auto-Optimization**
   - Self-tuning SQL
   - Dynamic caching
   - Smart prefetching

## Privacy Compliance

### GDPR Compliance

- ✅ No personal data collected
- ✅ Session IDs are anonymous
- ✅ 90-day retention period
- ✅ Right to deletion (via TTL)
- ✅ Data minimization
- ✅ Purpose limitation

### Data Processing Agreement

- Data stored in AWS
- Encrypted at rest and in transit
- Access controlled via IAM
- Audit logs available
- No third-party sharing

## Monitoring Learning System

### CloudWatch Metrics

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

# Track learning events
cloudwatch.put_metric_data(
    Namespace='FinOpsAgent',
    MetricData=[
        {
            'MetricName': 'QueriesLogged',
            'Value': 1,
            'Unit': 'Count'
        }
    ]
)
```

### Alerts

```bash
# Create alarm for low logging rate
aws cloudwatch put-metric-alarm \
  --alarm-name finops-agent-low-logging \
  --alarm-description "Alert when logging rate is low" \
  --metric-name QueriesLogged \
  --namespace FinOpsAgent \
  --statistic Sum \
  --period 3600 \
  --threshold 10 \
  --comparison-operator LessThanThreshold
```

## Best Practices

### 1. Data Quality

- ✅ Validate before logging
- ✅ Sanitize sensitive data
- ✅ Truncate long text
- ✅ Handle errors gracefully

### 2. Performance

- ✅ Log asynchronously
- ✅ Don't block user actions
- ✅ Batch writes when possible
- ✅ Use TTL for cleanup

### 3. Privacy

- ✅ Never log PII
- ✅ Anonymize session IDs
- ✅ Truncate responses
- ✅ Respect user privacy

### 4. Cost Optimization

- ✅ Use on-demand billing
- ✅ Enable TTL
- ✅ Monitor costs
- ✅ Archive old data

## Troubleshooting

### Logging Not Working

**Check:**
1. DynamoDB table exists
2. IAM permissions correct
3. AWS credentials configured
4. Network connectivity

**Solution:**
```bash
python scripts/setup_aws.py
```

### High DynamoDB Costs

**Optimize:**
1. Enable TTL (already enabled)
2. Use on-demand billing
3. Reduce retention period
4. Archive to S3

### Missing Data

**Verify:**
1. Logging functions called
2. No errors in logs
3. Table name correct
4. Region correct

## Summary

The learning system provides:

✅ **Automatic** - No manual intervention
✅ **Comprehensive** - Captures all interactions
✅ **Private** - No sensitive data stored
✅ **Actionable** - Insights for improvement
✅ **Scalable** - Handles any volume
✅ **Compliant** - GDPR-ready

The agent learns from every interaction to provide better insights, faster responses, and more relevant suggestions over time.

---

**The more you use it, the smarter it gets!** 🧠
