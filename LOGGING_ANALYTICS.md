# Logging & Analytics Documentation

## Overview

The FinOps GenAI Agent includes comprehensive logging and analytics capabilities to track user behavior, system performance, and usage patterns without storing uploaded files.

## What Gets Logged

### 1. Session Events

**Session Start**
- Session ID (unique identifier)
- Timestamp
- User agent
- Session start time

**Session End**
- Session duration
- Total queries made
- Total files uploaded
- Total chat messages

### 2. File Upload Events

**Logged Data:**
- File name (not content)
- File size
- Row count
- Column count
- Analysis type selected
- Timestamp

**NOT Logged:**
- Actual file content
- Data values
- Sensitive information

### 3. User Query Events

**Logged Data:**
- Query text
- Query length
- Whether it was a suggested prompt
- Analysis type
- Whether data was uploaded
- Timestamp

### 4. Agent Response Events

**Logged Data:**
- User query (for context)
- Response text (truncated to 1000 chars)
- Response length
- Processing time
- Whether visualization was generated
- Analysis type
- Data summary (metadata only)
- Timestamp

## Data Retention

- **TTL (Time To Live)**: 90 days
- Data automatically expires after 90 days
- Configurable in the code

## DynamoDB Schema

### Table Structure

**Table Name:** `finops-agent-interactions`

**Primary Key:** `interaction_id` (String)

### Item Types

#### Session Start
```json
{
  "interaction_id": "session_<uuid>",
  "timestamp": "2024-12-06T10:30:00Z",
  "event_type": "session_start",
  "session_id": "uuid",
  "session_start": "2024-12-06T10:30:00Z",
  "user_agent": "streamlit_app",
  "ttl": 1234567890
}
```

#### File Upload
```json
{
  "interaction_id": "upload_<session_id>_<count>",
  "timestamp": "2024-12-06T10:31:00Z",
  "event_type": "file_upload",
  "session_id": "uuid",
  "file_name": "cost_data.csv",
  "file_size": 1024000,
  "row_count": 500,
  "column_count": 10,
  "analysis_type": "Architecture Inference",
  "ttl": 1234567890
}
```

#### User Query
```json
{
  "interaction_id": "query_<session_id>_<count>",
  "timestamp": "2024-12-06T10:32:00Z",
  "event_type": "user_query",
  "session_id": "uuid",
  "user_query": "What are my top cost drivers?",
  "query_length": 28,
  "is_suggested_prompt": false,
  "analysis_type": "General Cost Analysis",
  "has_data": true,
  "ttl": 1234567890
}
```

#### Agent Response
```json
{
  "interaction_id": "response_<session_id>_<count>",
  "timestamp": "2024-12-06T10:32:05Z",
  "event_type": "agent_response",
  "session_id": "uuid",
  "user_query": "What are my top cost drivers?",
  "agent_response": "Based on your data, the top 3 cost drivers are...",
  "response_length": 1500,
  "processing_time": 4.5,
  "has_visualization": true,
  "analysis_type": "General Cost Analysis",
  "data_summary": "{\"total_cost\": 5000, \"rows\": 500}",
  "ttl": 1234567890
}
```

#### Session End
```json
{
  "interaction_id": "session_end_<session_id>",
  "timestamp": "2024-12-06T11:00:00Z",
  "event_type": "session_end",
  "session_id": "uuid",
  "session_duration": 1800,
  "total_queries": 5,
  "total_uploads": 1,
  "chat_messages": 10,
  "ttl": 1234567890
}
```

## Analytics Dashboard

### Running the Dashboard

```bash
streamlit run analytics_dashboard.py
```

### Features

1. **Key Metrics**
   - Total sessions
   - Total queries
   - Files uploaded
   - Average response time
   - Average session duration
   - Queries per session
   - Completion rate

2. **Activity Over Time**
   - Daily activity chart
   - Event type breakdown
   - Trend analysis

3. **Analysis Type Distribution**
   - Query distribution by type
   - Upload distribution by type
   - Pie charts for visualization

4. **Query Patterns**
   - Suggested vs custom queries
   - Responses with visualizations
   - Usage patterns

5. **File Upload Statistics**
   - File size distribution
   - Row count distribution
   - Upload frequency

6. **Recent Activity**
   - Last 20 events
   - Event details
   - Session tracking

7. **Data Export**
   - Export to CSV
   - Full analytics data
   - Custom date ranges

## Privacy & Security

### What We DON'T Store

- ❌ Actual file content
- ❌ Sensitive data values
- ❌ Personal information
- ❌ AWS credentials
- ❌ Full response text (truncated)

### What We DO Store

- ✅ Metadata only
- ✅ Usage patterns
- ✅ Performance metrics
- ✅ Session information
- ✅ Query text (for learning)

### Security Measures

1. **Data Encryption**
   - DynamoDB encryption at rest
   - TLS for data in transit

2. **Access Control**
   - IAM policies
   - Least privilege access
   - No public access

3. **Data Retention**
   - 90-day TTL
   - Automatic expiration
   - No long-term storage

4. **Anonymization**
   - Session IDs (not user IDs)
   - No PII collection
   - Aggregated analytics

## Use Cases

### 1. Usage Analytics

**Questions Answered:**
- How many users are using the app?
- What features are most popular?
- When is peak usage time?
- What analysis types are common?

### 2. Performance Monitoring

**Metrics Tracked:**
- Response times
- Processing duration
- Error rates
- System health

### 3. User Behavior

**Insights:**
- Common query patterns
- Suggested vs custom prompts
- Session duration
- Feature adoption

### 4. Product Improvement

**Data-Driven Decisions:**
- Which features to enhance
- What prompts to add
- UI/UX improvements
- Performance optimization

## Querying Analytics Data

### Using AWS CLI

```bash
# Get all events for a session
aws dynamodb query \
  --table-name finops-agent-interactions \
  --index-name session-id-index \
  --key-condition-expression "session_id = :sid" \
  --expression-attribute-values '{":sid":{"S":"your-session-id"}}'

# Scan recent events
aws dynamodb scan \
  --table-name finops-agent-interactions \
  --filter-expression "event_type = :type" \
  --expression-attribute-values '{":type":{"S":"user_query"}}'
```

### Using Python (Boto3)

```python
import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('finops-agent-interactions')

# Get recent queries
response = table.scan(
    FilterExpression='event_type = :type',
    ExpressionAttributeValues={':type': 'user_query'}
)

queries = response['Items']
```

## Custom Analytics

### Adding Custom Events

```python
def log_custom_event(event_name, event_data):
    """Log custom analytics event"""
    try:
        dynamodb = get_dynamodb_client()
        table = dynamodb.Table('finops-agent-interactions')
        
        item = {
            'interaction_id': f"custom_{event_name}_{timestamp}",
            'timestamp': datetime.now().isoformat(),
            'event_type': 'custom_event',
            'event_name': event_name,
            'event_data': json.dumps(event_data),
            'session_id': st.session_state.session_id,
            'ttl': int((datetime.now().timestamp() + 90*24*60*60))
        }
        
        table.put_item(Item=item)
    except Exception as e:
        pass
```

### Example Custom Events

```python
# Log feature usage
log_custom_event('feature_used', {
    'feature': 'export_to_pdf',
    'success': True
})

# Log error
log_custom_event('error_occurred', {
    'error_type': 'bedrock_timeout',
    'error_message': 'Request timed out'
})

# Log user feedback
log_custom_event('user_feedback', {
    'rating': 5,
    'comment': 'Very helpful!'
})
```

## Compliance

### GDPR Compliance

- No personal data collected
- Session IDs are anonymous
- 90-day retention period
- Right to deletion (via TTL)

### Data Processing Agreement

- Data stored in AWS
- Encrypted at rest and in transit
- Access controlled via IAM
- Audit logs available

## Monitoring & Alerts

### CloudWatch Integration

```python
# Send metrics to CloudWatch
import boto3

cloudwatch = boto3.client('cloudwatch')

cloudwatch.put_metric_data(
    Namespace='FinOpsAgent',
    MetricData=[
        {
            'MetricName': 'QueryCount',
            'Value': 1,
            'Unit': 'Count',
            'Timestamp': datetime.now()
        }
    ]
)
```

### Setting Up Alerts

```bash
# Create alarm for high error rate
aws cloudwatch put-metric-alarm \
  --alarm-name finops-agent-high-errors \
  --alarm-description "Alert when error rate is high" \
  --metric-name ErrorRate \
  --namespace FinOpsAgent \
  --statistic Average \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold
```

## Best Practices

1. **Regular Review**
   - Check analytics weekly
   - Monitor performance trends
   - Identify issues early

2. **Data Cleanup**
   - TTL handles automatic cleanup
   - No manual intervention needed
   - 90-day retention is sufficient

3. **Privacy First**
   - Never log sensitive data
   - Truncate long responses
   - Use session IDs, not user IDs

4. **Performance**
   - Log asynchronously
   - Don't block user actions
   - Silent failures for logging

5. **Cost Optimization**
   - Use on-demand billing
   - Enable TTL for auto-cleanup
   - Monitor DynamoDB costs

## Troubleshooting

### Logging Not Working

**Check:**
1. DynamoDB table exists
2. IAM permissions correct
3. AWS credentials configured
4. Network connectivity

### Analytics Dashboard Empty

**Solutions:**
1. Use the app to generate data
2. Check date range filter
3. Verify DynamoDB access
4. Check for errors in logs

### High DynamoDB Costs

**Optimize:**
1. Enable TTL (already enabled)
2. Use on-demand billing
3. Reduce retention period
4. Archive old data to S3

---

**For more information:**
- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [CloudWatch Metrics](https://docs.aws.amazon.com/cloudwatch/)
- [Privacy Best Practices](https://aws.amazon.com/compliance/data-privacy/)
