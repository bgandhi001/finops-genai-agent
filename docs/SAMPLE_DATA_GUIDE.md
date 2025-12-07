# Sample Data Guide

## Overview

The FinOps GenAI Agent includes comprehensive sample datasets to help you test and train the agent without needing actual AWS data. These datasets cover common FinOps scenarios and optimization opportunities.

## Available Datasets

### 1. EBS Volumes (Unattached) - `sample_ebs_volumes.csv`

**Purpose:** Identify unattached EBS volumes that are incurring costs without providing value.

**Key Metrics:**
- 150 total volumes
- ~30% unattached (available state)
- Potential savings: $2,000-3,000/month
- Multiple volume types (gp2, gp3, io1, io2, st1, sc1)

**Columns:**
- `volume_id` - Unique volume identifier
- `volume_type` - EBS volume type (gp2, gp3, io1, etc.)
- `size_gb` - Volume size in gigabytes
- `state` - Volume state (available = unattached, in-use = attached)
- `region` - AWS region
- `availability_zone` - Specific AZ
- `create_date` - When volume was created
- `days_unattached` - How long volume has been unattached
- `monthly_cost` - Current monthly cost
- `wasted_cost` - Cost wasted due to being unattached
- `iops` - Provisioned IOPS (for io1/io2)
- `throughput_mbps` - Provisioned throughput (for gp3)
- `last_attached_instance` - Last EC2 instance it was attached to
- `snapshot_id` - Associated snapshot (if any)
- `encrypted` - Whether volume is encrypted
- `tags_project` - Project tag
- `tags_environment` - Environment tag

**Sample Questions to Ask:**
- "Show me all unattached EBS volumes"
- "What's the total cost of unattached volumes?"
- "Which volume types are most commonly unattached?"
- "Show me volumes unattached for more than 90 days"
- "What's the potential monthly savings from deleting unattached volumes?"
- "Which projects have the most unattached volumes?"

**Expected Insights:**
- Identify volumes that can be safely deleted
- Find volumes that should be converted to snapshots
- Detect gp2 volumes that should be upgraded to gp3
- Discover over-provisioned IOPS

### 2. S3 Buckets (Unused) - `sample_s3_buckets.csv`

**Purpose:** Find S3 buckets with no GET/PUT operations that may be candidates for deletion or archival.

**Key Metrics:**
- 80 total buckets
- ~35% with no activity (0 GET/PUT requests)
- Potential savings: $1,000-1,500/month
- Various storage classes

**Columns:**
- `bucket_name` - Unique bucket name
- `region` - AWS region
- `storage_class` - Storage class (STANDARD, STANDARD_IA, GLACIER, etc.)
- `size_gb` - Total bucket size in GB
- `object_count` - Number of objects
- `create_date` - When bucket was created
- `last_modified_date` - Last time objects were modified
- `days_inactive` - Days since last activity
- `get_requests_30d` - GET requests in last 30 days
- `put_requests_30d` - PUT requests in last 30 days
- `monthly_storage_cost` - Storage cost per month
- `monthly_request_cost` - Request cost per month
- `total_monthly_cost` - Total monthly cost
- `wasted_cost` - Cost wasted on inactive bucket
- `versioning_enabled` - Whether versioning is on
- `lifecycle_policy` - Whether lifecycle policy exists
- `public_access` - Whether bucket is public
- `encryption` - Encryption type (AES256, aws:kms)
- `tags_project` - Project tag
- `tags_owner` - Owner tag

**Sample Questions to Ask:**
- "Show me S3 buckets with no activity in the last 90 days"
- "What's the total cost of unused S3 buckets?"
- "Which buckets have no GET or PUT requests?"
- "Show me large buckets with no activity"
- "Which storage class is most common for inactive buckets?"
- "Find buckets that should be moved to Glacier"
- "Show me public buckets with no activity"

**Expected Insights:**
- Identify buckets that can be deleted
- Find buckets that should be archived to Glacier
- Detect buckets in wrong storage class
- Discover buckets without lifecycle policies
- Find security risks (public buckets)

### 3. Monthly Trends - `sample_monthly_trends.csv`

**Purpose:** Analyze cost trends over 12 months to identify patterns, anomalies, and forecast future costs.

**Key Metrics:**
- 12 months of historical data
- 10 AWS services tracked
- 4 regions covered
- 480 total data points

**Services Included:**
- Amazon EC2 (increasing trend, 5% monthly growth)
- Amazon RDS (stable)
- Amazon S3 (increasing trend)
- Amazon DynamoDB (increasing trend)
- AWS Lambda (increasing trend)
- Amazon CloudFront (stable)
- Amazon EBS (increasing trend)
- Amazon ElastiCache (stable)
- NAT Gateway (stable)
- Elastic Load Balancing (stable)

**Columns:**
- `month` - Month in YYYY-MM format
- `service` - AWS service name
- `region` - AWS region
- `monthly_cost` - Total cost for the month
- `usage_hours` - Total usage hours
- `resource_count` - Number of resources
- `avg_cost_per_resource` - Average cost per resource
- `cost_change_pct` - Percentage change from previous month
- `forecast_next_month` - Forecasted cost for next month

**Sample Questions to Ask:**
- "Show me cost trends for EC2 over the last 12 months"
- "Which services have increasing costs?"
- "What's the month-over-month growth rate for each service?"
- "Show me services with the highest cost volatility"
- "Which region has the highest cost growth?"
- "Forecast next month's costs for all services"
- "Show me services where costs are stable"
- "Which service has the highest cost per resource?"

**Expected Insights:**
- Identify services with unexpected cost growth
- Detect seasonal patterns
- Forecast future costs
- Find optimization opportunities
- Compare regional costs
- Track resource efficiency

### 4. Architecture Inference - `sample_architecture_data.csv`

**Purpose:** Detect architectural inefficiencies from billing patterns.

**Key Scenarios:**
- High cross-AZ data transfer (chatty microservices)
- NAT Gateway usage vs VPC Endpoints
- Legacy volume types (gp2 vs gp3)

**Sample Questions:**
- "Show me cross-region data transfer costs"
- "Which resources have high NAT Gateway usage?"
- "Find gp2 volumes that should be upgraded to gp3"

### 5. Tagging Correlation - `sample_tagging_data.csv`

**Purpose:** Find untagged resources and correlate them with tagged resources created at the same time.

**Key Features:**
- Untagged resources
- Time-based correlation
- Ownership probability

**Sample Questions:**
- "Show me untagged resources"
- "Which project likely owns this untagged volume?"
- "Find resources created at the same time"

### 6. General Cost Analysis - `sample_cost_analysis.csv`

**Purpose:** General cost analysis across services and regions over 30 days.

**Sample Questions:**
- "What are my top cost drivers?"
- "Show me daily cost trends"
- "Which region is most expensive?"

## Using Sample Data

### Quick Start

1. **Generate Sample Data:**
   ```bash
   source venv/bin/activate
   python scripts/generate_sample_data.py
   ```

2. **Start the App:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Upload a Dataset:**
   - Click "Upload CSV file"
   - Select any file from `sample_data/` folder
   - Agent will auto-detect the data type

4. **Ask Questions:**
   - Use suggested prompts
   - Or ask your own questions
   - Agent will generate SQL and analyze

### Training the Agent

The agent learns from every interaction. To train it effectively:

1. **Upload Different Datasets:**
   - Start with EBS volumes
   - Then try S3 buckets
   - Then monthly trends
   - Mix and match

2. **Ask Diverse Questions:**
   - Cost analysis: "What's the total cost?"
   - Optimization: "Show me savings opportunities"
   - Trends: "How are costs changing?"
   - Comparisons: "Compare regions"

3. **Use Suggested Prompts:**
   - Agent generates contextual questions
   - These help train pattern recognition
   - Try variations of suggested prompts

4. **Review SQL Queries:**
   - Check generated SQL in expander
   - Understand how agent translates questions
   - Learn what works best

5. **Iterate and Refine:**
   - Ask follow-up questions
   - Drill into specific areas
   - Build on previous answers

### Best Practices

**For Testing:**
- Start with smaller datasets (EBS, S3)
- Test one scenario at a time
- Verify SQL queries are correct
- Check visualizations make sense

**For Training:**
- Upload all datasets over time
- Ask similar questions in different ways
- Use both suggested and custom prompts
- Review analytics dashboard regularly

**For Demonstrations:**
- Use monthly trends for executive views
- Use EBS/S3 for optimization stories
- Use architecture data for technical discussions
- Combine datasets for comprehensive analysis

## Data Characteristics

### Realism

All sample data is designed to be realistic:
- ✅ Actual AWS service names
- ✅ Real pricing models
- ✅ Typical usage patterns
- ✅ Common optimization scenarios
- ✅ Realistic cost ranges

### Variety

Data includes diverse scenarios:
- ✅ Multiple regions
- ✅ Different resource types
- ✅ Various cost levels
- ✅ Different time periods
- ✅ Tagged and untagged resources

### Optimization Opportunities

Each dataset includes clear optimization opportunities:
- ✅ Unattached volumes to delete
- ✅ Unused buckets to archive
- ✅ Growing costs to investigate
- ✅ Inefficient architectures to fix
- ✅ Untagged resources to label

## Regenerating Data

To generate fresh sample data:

```bash
source venv/bin/activate
python scripts/generate_sample_data.py
```

This will:
- Create new random data
- Overwrite existing files
- Generate different patterns
- Provide variety for testing

## Custom Data

To create your own sample data:

1. **Copy the generator script:**
   ```bash
   cp scripts/generate_sample_data.py scripts/my_custom_data.py
   ```

2. **Modify the functions:**
   - Adjust data ranges
   - Change column names
   - Add new metrics
   - Customize scenarios

3. **Run your script:**
   ```bash
   python scripts/my_custom_data.py
   ```

## Analytics Dashboard

View learning data from sample uploads:

```bash
streamlit run analytics_dashboard.py
```

This shows:
- Most common questions
- Query patterns
- Response times
- Service distribution
- Usage trends

## Summary

The sample datasets provide:

✅ **Realistic Data** - Based on actual AWS patterns
✅ **Diverse Scenarios** - Multiple optimization opportunities
✅ **Training Material** - Helps agent learn patterns
✅ **Testing Coverage** - Validates all features
✅ **Demo Ready** - Professional examples

Use these datasets to explore the agent's capabilities, train it on your specific use cases, and demonstrate FinOps value to stakeholders!

---

**Generated with ❤️ for FinOps practitioners**
