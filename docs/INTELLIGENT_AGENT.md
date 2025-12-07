# Intelligent AWS Agent Documentation

## Overview

The Intelligent AWS Agent is a smart, adaptive system that can analyze **ANY** AWS service SQL output, automatically understand the data structure, detect the AWS service, and generate contextual insights and questions.

## Key Features

### 🧠 Automatic Service Detection

The agent automatically detects which AWS service your data is from:

- **EC2** - Instances, AMIs, availability zones
- **S3** - Buckets, storage, objects
- **RDS** - Databases, engines, instances
- **Lambda** - Functions, invocations, duration
- **DynamoDB** - Tables, capacity, throughput
- **CloudFront** - Distributions, edge locations
- **EBS** - Volumes, snapshots, GP2/GP3
- **VPC** - Subnets, NAT gateways, endpoints
- **ELB/ALB/NLB** - Load balancers, targets
- **Cost & Usage Report** - Billing data
- **IAM** - Users, roles, policies
- **Route53** - DNS, hosted zones
- **SQS/SNS** - Queues, topics, messages
- **ECS/EKS** - Containers, clusters, tasks
- **Athena** - Query executions
- **Glue** - Crawlers, jobs, catalog
- **Redshift** - Clusters, warehouses
- And more...

### 📊 Intelligent Column Classification

Automatically classifies columns into:

1. **Identifiers** - IDs, ARNs, account numbers
2. **Metrics** - Numeric measurements
3. **Costs** - Cost, charge, price columns
4. **Dimensions** - Categorical data
5. **Timestamps** - Date/time fields
6. **Tags** - Resource tags

### 💡 Smart Question Generation

Generates contextual questions based on:
- Detected AWS service
- Available columns
- Data structure
- Cost information
- Time series data

### 📈 Automatic Data Profiling

Creates comprehensive data profile:
- Row and column counts
- Data types
- Missing values
- Sample values
- Unique value counts
- Numeric statistics

### 🎯 Context-Aware Analysis

Generates enhanced prompts for the LLM that include:
- Service-specific context
- Column classifications
- Sample data
- Relevant AWS best practices

## How It Works

### 1. Data Upload

```python
# User uploads CSV file
df = pd.read_csv(uploaded_file)
```

### 2. Automatic Analysis

```python
agent = IntelligentAWSAgent()
analysis = agent.analyze_data(df)

# Returns:
{
    'service': 'EC2',  # Detected service
    'profile': {...},   # Data profile
    'column_types': {...}  # Column classifications
}
```

### 3. Smart Question Generation

```python
questions = agent.generate_smart_questions()

# Returns contextual questions like:
[
    "💰 What are the top 5 cost drivers in this EC2 data?",
    "🖥️ Which instance types are most used?",
    "🌍 Show me distribution across availability zones",
    ...
]
```

### 4. Enhanced Analysis

```python
prompt, context = agent.generate_analysis_prompt(user_query)

# Generates comprehensive prompt with:
# - Service context
# - Column classifications
# - Sample data
# - AWS best practices
```

## Usage Examples

### Example 1: EC2 Cost Analysis

**Input CSV:**
```csv
instance_id,instance_type,availability_zone,usage_hours,cost
i-123,t3.medium,us-east-1a,720,52.00
i-456,m5.large,us-east-1b,720,104.00
```

**Agent Detection:**
- Service: EC2
- Cost columns: cost
- Metrics: usage_hours
- Dimensions: instance_type, availability_zone
- Identifiers: instance_id

**Generated Questions:**
- 💰 What are the top 5 cost drivers in this EC2 data?
- 🖥️ Which instance types are most used?
- 🌍 Show me distribution across availability zones
- 💡 Are there any underutilized instances?

### Example 2: S3 Storage Analysis

**Input CSV:**
```csv
bucket_name,storage_gb,requests,cost,region
my-bucket-1,1024,50000,23.55,us-east-1
my-bucket-2,2048,100000,47.10,us-west-2
```

**Agent Detection:**
- Service: S3
- Cost columns: cost
- Metrics: storage_gb, requests
- Dimensions: bucket_name, region

**Generated Questions:**
- 🪣 Which buckets have the highest storage costs?
- 📦 What's the total storage size?
- 🔄 Identify opportunities for lifecycle policies
- 📊 Show me a breakdown of cost by region

### Example 3: Lambda Function Analysis

**Input CSV:**
```csv
function_name,invocations,duration_ms,memory_mb,cost
process-orders,100000,250,512,15.50
send-emails,50000,100,256,5.25
```

**Agent Detection:**
- Service: Lambda
- Cost columns: cost
- Metrics: invocations, duration_ms, memory_mb
- Dimensions: function_name

**Generated Questions:**
- ⚡ Which functions have the highest invocation count?
- ⏱️ What's the average execution duration?
- 💰 Which functions are most expensive?
- 🎯 Identify optimization opportunities

## API Reference

### IntelligentAWSAgent Class

#### `analyze_data(df)`

Analyzes uploaded DataFrame and returns comprehensive analysis.

**Parameters:**
- `df` (DataFrame): Pandas DataFrame with AWS data

**Returns:**
```python
{
    'service': str,  # Detected AWS service
    'profile': dict,  # Data profile
    'column_types': dict  # Column classifications
}
```

#### `generate_smart_questions()`

Generates contextual questions based on data analysis.

**Returns:**
- List of strings (questions)

#### `generate_analysis_prompt(user_query)`

Creates enhanced prompt for LLM with full context.

**Parameters:**
- `user_query` (str): User's question

**Returns:**
- Tuple: (prompt, context)

#### `create_summary_table()`

Generates summary statistics table.

**Returns:**
- Dictionary with key metrics

#### `get_aggregation_suggestions()`

Suggests useful data aggregations.

**Returns:**
- List of aggregation suggestions

#### `perform_aggregation(agg_type, metric, group_by)`

Performs data aggregation.

**Parameters:**
- `agg_type` (str): 'sum', 'mean', or 'count'
- `metric` (str): Column to aggregate
- `group_by` (str): Column to group by

**Returns:**
- Dictionary with aggregated results

## Service Detection Logic

### Pattern Matching

The agent uses keyword matching to detect services:

```python
service_patterns = {
    'EC2': ['instance', 'ec2', 'availability_zone', 'instance_type', 'ami'],
    'S3': ['bucket', 's3', 'storage', 'object'],
    'RDS': ['rds', 'database', 'db_instance', 'engine'],
    # ... more patterns
}
```

### Cost Detection

Special handling for Cost & Usage Report:

```python
# If cost-related columns found
if 'line_item' in columns or 'unblended_cost' in columns:
    return 'Cost & Usage Report'
```

### Confidence Scoring

Requires at least 2 pattern matches for service detection.

## Column Classification Logic

### Identifiers

Keywords: `id`, `arn`, `resource_id`, `account`

### Costs

Keywords: `cost`, `charge`, `price`
Type: Numeric

### Metrics

Type: Numeric (excluding costs)

### Timestamps

Keywords: `date`, `time`, `timestamp`, `created`, `modified`

### Tags

Keywords: `tag`

### Dimensions

Everything else (categorical data)

## Question Generation Strategy

### Cost-Based Questions

If cost columns exist:
- Top cost drivers
- Cost breakdowns
- Optimization opportunities
- Total cost analysis

### Time-Series Questions

If timestamp columns exist:
- Trends over time
- Pattern identification
- Anomaly detection
- Spike analysis

### Service-Specific Questions

Based on detected service:
- EC2: Instance types, AZ distribution
- S3: Bucket costs, storage size
- Lambda: Invocations, duration
- RDS: Database costs, performance

### Dimension-Based Questions

Based on available dimensions:
- Group by analysis
- Top values
- Distribution analysis

### General Questions

Always included:
- Key insights summary
- Action plan
- Quick wins
- Comprehensive report

## Integration with Streamlit App

### Initialization

```python
if 'intelligent_agent' not in st.session_state:
    st.session_state.intelligent_agent = IntelligentAWSAgent()
```

### Data Analysis

```python
agent = st.session_state.intelligent_agent
analysis = agent.analyze_data(df)
```

### Question Display

```python
questions = agent.generate_smart_questions()
for question in questions:
    if st.button(question):
        # Process question
```

### Enhanced LLM Calls

```python
prompt, context = agent.generate_analysis_prompt(user_query)
response = call_bedrock_llm(prompt, context, chat_history)
```

## Customization

### Adding New Services

```python
# In _detect_aws_service method
service_patterns = {
    'YourService': ['keyword1', 'keyword2', 'keyword3'],
    # ...
}
```

### Custom Questions

```python
# In generate_smart_questions method
if service == 'YourService':
    questions.extend([
        "Your custom question 1",
        "Your custom question 2"
    ])
```

### Custom Column Types

```python
# In _classify_columns method
if 'your_pattern' in col_lower:
    classification['your_type'].append(col)
```

## Best Practices

### 1. Data Quality

- Ensure CSV has headers
- Use consistent column naming
- Include relevant columns for detection

### 2. Column Naming

Use AWS-standard naming:
- `instance_id` not `id`
- `unblended_cost` not `price`
- `availability_zone` not `az`

### 3. Data Size

- Works best with 100-10,000 rows
- Samples first 20 rows for analysis
- Aggregates large datasets

### 4. Service Detection

- Include service-specific columns
- Use standard AWS terminology
- Add cost columns for better detection

## Troubleshooting

### Service Not Detected

**Problem:** Shows "Unknown AWS Service"

**Solutions:**
1. Check column names match AWS patterns
2. Add more service-specific columns
3. Manually specify service in code

### No Questions Generated

**Problem:** Empty question list

**Solutions:**
1. Ensure data is uploaded
2. Check data has valid columns
3. Verify data analysis completed

### Poor Question Quality

**Problem:** Generic questions

**Solutions:**
1. Add more descriptive columns
2. Include cost/metric columns
3. Use standard AWS naming

## Performance

### Analysis Speed

- Data profiling: < 1 second
- Service detection: < 0.1 seconds
- Question generation: < 0.5 seconds
- Total: < 2 seconds for typical datasets

### Memory Usage

- Minimal overhead
- Stores only metadata
- No data duplication

### Scalability

- Handles up to 100K rows
- Efficient column classification
- Optimized aggregations

## Future Enhancements

### Planned Features

1. **ML-Based Detection**
   - Train model on AWS data patterns
   - Improve detection accuracy
   - Handle edge cases

2. **Custom Service Definitions**
   - User-defined services
   - Custom patterns
   - Configurable questions

3. **Advanced Aggregations**
   - Multi-level grouping
   - Complex calculations
   - Statistical analysis

4. **Query Builder**
   - Visual query interface
   - Drag-and-drop aggregations
   - Export to SQL

5. **Data Validation**
   - Schema validation
   - Data quality checks
   - Anomaly detection

## Examples

See `generate_sample_data.py` for example datasets that work with the intelligent agent.

## Support

For issues or questions:
- GitHub Issues: https://github.com/bgandhi001/finops-genai-agent/issues
- Documentation: README_STREAMLIT.md
- Examples: QUICKSTART.md

---

**The Intelligent Agent makes your FinOps analysis smarter, faster, and more accurate!** 🚀
