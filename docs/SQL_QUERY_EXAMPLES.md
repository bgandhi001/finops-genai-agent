# SQL Query Examples Feature

## Overview

The FinOps GenAI Agent now automatically generates example SQL queries tailored to your uploaded data. This feature helps you learn SQL, understand your data structure, and perform precise analysis without relying solely on natural language queries.

## How It Works

### 1. Automatic Generation

When you upload a CSV file, the agent:
- ✅ Analyzes your data structure
- ✅ Identifies column types (costs, metrics, dimensions, dates)
- ✅ Detects AWS service type
- ✅ Generates relevant SQL examples
- ✅ Organizes queries by category

### 2. Smart Categorization

Queries are grouped into categories:
- **Basic Analysis** - Simple queries to get started
- **Cost Analysis** - Cost-focused queries
- **Trend Analysis** - Time-based analysis
- **Optimization** - Find savings opportunities
- **Metrics Analysis** - Performance metrics
- **Filtering** - Focus on specific data
- **Advanced** - Complex analytical queries
- **Service-Specific** - Tailored to EC2, S3, RDS, etc.

### 3. Interactive Interface

Each example includes:
- **Description** - What the query does
- **Use Case** - When to use it
- **SQL Code** - Ready-to-execute query
- **Copy Button** - One-click copy to editor

## Example Categories

### Basic Analysis

**View Sample Data**
```sql
SELECT * FROM aws_data LIMIT 10
```
Use case: Quick preview of your data

**Count Total Rows**
```sql
SELECT COUNT(*) as total_rows FROM aws_data
```
Use case: Understand data volume

### Cost Analysis

**Total Cost Summary**
```sql
SELECT 
    SUM(cost) as total_cost,
    AVG(cost) as avg_cost,
    MAX(cost) as max_cost,
    MIN(cost) as min_cost
FROM aws_data
```
Use case: Get overall cost statistics

**Top 10 Costs by Service**
```sql
SELECT 
    service,
    SUM(cost) as total_cost,
    COUNT(*) as count
FROM aws_data
GROUP BY service
ORDER BY total_cost DESC
LIMIT 10
```
Use case: Identify highest cost services

**Multi-Dimensional Cost Breakdown**
```sql
SELECT 
    service,
    region,
    SUM(cost) as total_cost
FROM aws_data
GROUP BY service, region
ORDER BY total_cost DESC
LIMIT 20
```
Use case: Analyze costs across multiple dimensions

### Trend Analysis

**Daily Cost Trends**
```sql
SELECT 
    date,
    SUM(cost) as daily_cost,
    COUNT(*) as records
FROM aws_data
GROUP BY date
ORDER BY date
```
Use case: Track cost changes over time

**Cost Trends by Service**
```sql
SELECT 
    date,
    service,
    SUM(cost) as cost
FROM aws_data
GROUP BY date, service
ORDER BY date, cost DESC
```
Use case: Track service costs over time

### Optimization Queries

**Find Unattached/Unused Resources**
```sql
SELECT 
    *
FROM aws_data
WHERE LOWER(state) IN ('available', 'unused', 'stopped')
```
Use case: Identify resources that can be deleted

**Resources with Zero or Minimal Cost**
```sql
SELECT 
    service,
    cost
FROM aws_data
WHERE cost < 1
ORDER BY cost
```
Use case: Find low-value resources

### Metrics Analysis

**Average Metrics by Dimension**
```sql
SELECT 
    service,
    AVG(usage_amount) as avg_metric,
    MAX(usage_amount) as max_metric,
    MIN(usage_amount) as min_metric
FROM aws_data
GROUP BY service
ORDER BY avg_metric DESC
```
Use case: Analyze metric distribution

### Filtering Queries

**Filter by Specific Value**
```sql
SELECT 
    *
FROM aws_data
WHERE service = 'Amazon EC2'
LIMIT 100
```
Use case: Focus on specific service

### Advanced Queries

**Cost Distribution Percentiles**
```sql
SELECT 
    service,
    SUM(cost) as total_cost,
    ROUND(100.0 * SUM(cost) / SUM(SUM(cost)) OVER (), 2) as cost_percentage
FROM aws_data
GROUP BY service
ORDER BY total_cost DESC
```
Use case: Understand cost distribution

**Resources Above Average Cost**
```sql
SELECT 
    *
FROM aws_data
WHERE cost > (SELECT AVG(cost) FROM aws_data)
ORDER BY cost DESC
```
Use case: Find expensive outliers

### Service-Specific Queries

**EC2/EBS: Group by Volume Type**
```sql
SELECT 
    volume_type,
    COUNT(*) as count,
    SUM(size_gb) as total_size_gb
FROM aws_data
GROUP BY volume_type
ORDER BY count DESC
```
Use case: Analyze volume type distribution

**S3: Buckets by Storage Class**
```sql
SELECT 
    storage_class,
    COUNT(*) as bucket_count,
    SUM(size_gb) as total_size_gb
FROM aws_data
GROUP BY storage_class
ORDER BY total_size_gb DESC
```
Use case: Analyze storage class usage

## Usage Workflow

### Step 1: Upload Data

Upload your CSV file (CUR, Trusted Advisor, inventory data, etc.)

### Step 2: Open Example Queries

Click "📚 Example SQL Queries - Learn by Example" expander

### Step 3: Browse Categories

Navigate through tabs:
- Basic Analysis
- Cost Analysis
- Trend Analysis
- Optimization
- Advanced
- Service-Specific

### Step 4: Copy Query

Click "📋 Copy" button next to any query

### Step 5: Execute

Query is automatically pasted into the SQL editor. Click "▶️ Execute SQL"

### Step 6: Modify

Customize the query for your specific needs:
- Change column names
- Adjust filters
- Modify aggregations
- Add WHERE clauses

### Step 7: Visualize

Results are automatically displayed with:
- Data table
- Download button
- Visualization options (bar, line, pie, scatter)

## Learning Path

### Beginner

Start with Basic Analysis:
1. View sample data
2. Count rows
3. Simple aggregations

### Intermediate

Move to Cost Analysis:
1. Total cost summary
2. Top costs by dimension
3. Multi-dimensional breakdowns

### Advanced

Explore complex queries:
1. Percentile calculations
2. Window functions
3. Subqueries
4. Joins (when multiple files)

## Customization Tips

### Modify Filters

**Original:**
```sql
SELECT * FROM aws_data LIMIT 10
```

**Modified:**
```sql
SELECT * FROM aws_data 
WHERE region = 'us-east-1' 
  AND cost > 100
LIMIT 10
```

### Add Calculations

**Original:**
```sql
SELECT service, SUM(cost) as total_cost
FROM aws_data
GROUP BY service
```

**Modified:**
```sql
SELECT 
    service, 
    SUM(cost) as total_cost,
    AVG(cost) as avg_cost,
    COUNT(*) as resource_count,
    SUM(cost) / COUNT(*) as cost_per_resource
FROM aws_data
GROUP BY service
ORDER BY total_cost DESC
```

### Combine Conditions

**Original:**
```sql
SELECT * FROM aws_data WHERE state = 'available'
```

**Modified:**
```sql
SELECT * FROM aws_data 
WHERE state = 'available' 
  AND cost > 10
  AND region IN ('us-east-1', 'us-west-2')
ORDER BY cost DESC
```

### Add Time Ranges

**Original:**
```sql
SELECT date, SUM(cost) FROM aws_data GROUP BY date
```

**Modified:**
```sql
SELECT 
    date, 
    SUM(cost) as daily_cost
FROM aws_data
WHERE date >= '2024-01-01' 
  AND date <= '2024-12-31'
GROUP BY date
ORDER BY date
```

## Common Use Cases

### 1. Find Top Cost Drivers

**Goal:** Identify what's costing the most

**Query:**
```sql
SELECT 
    service,
    region,
    SUM(cost) as total_cost,
    COUNT(*) as resource_count
FROM aws_data
GROUP BY service, region
ORDER BY total_cost DESC
LIMIT 20
```

### 2. Detect Unused Resources

**Goal:** Find resources to delete

**Query:**
```sql
SELECT 
    resource_id,
    service,
    state,
    cost,
    days_unused
FROM aws_data
WHERE state IN ('available', 'stopped', 'unused')
  AND days_unused > 30
ORDER BY cost DESC
```

### 3. Month-over-Month Growth

**Goal:** Track cost trends

**Query:**
```sql
SELECT 
    DATE_TRUNC('month', date) as month,
    service,
    SUM(cost) as monthly_cost
FROM aws_data
GROUP BY month, service
ORDER BY month, monthly_cost DESC
```

### 4. Cost Anomalies

**Goal:** Find unusual spikes

**Query:**
```sql
SELECT 
    date,
    service,
    cost,
    AVG(cost) OVER (PARTITION BY service) as avg_cost
FROM aws_data
WHERE cost > (SELECT AVG(cost) * 2 FROM aws_data)
ORDER BY cost DESC
```

### 5. Resource Efficiency

**Goal:** Calculate cost per unit

**Query:**
```sql
SELECT 
    service,
    SUM(cost) as total_cost,
    SUM(usage_amount) as total_usage,
    SUM(cost) / NULLIF(SUM(usage_amount), 0) as cost_per_unit
FROM aws_data
GROUP BY service
ORDER BY cost_per_unit DESC
```

## Best Practices

### 1. Start Simple

Begin with basic queries and gradually add complexity:
```sql
-- Start
SELECT * FROM aws_data LIMIT 10

-- Add filter
SELECT * FROM aws_data WHERE service = 'EC2' LIMIT 10

-- Add aggregation
SELECT service, COUNT(*) FROM aws_data GROUP BY service

-- Add sorting
SELECT service, COUNT(*) as count 
FROM aws_data 
GROUP BY service 
ORDER BY count DESC
```

### 2. Use LIMIT

Always use LIMIT when exploring:
```sql
SELECT * FROM aws_data LIMIT 100
```

### 3. Test Filters First

Verify your WHERE clause:
```sql
-- Check what you're filtering
SELECT DISTINCT service FROM aws_data

-- Then apply filter
SELECT * FROM aws_data WHERE service = 'Amazon EC2'
```

### 4. Comment Your Queries

Add comments for clarity:
```sql
-- Find top 10 EC2 costs by instance type
-- Excludes stopped instances
SELECT 
    instance_type,
    SUM(cost) as total_cost  -- Sum across all regions
FROM aws_data
WHERE service = 'Amazon EC2'
  AND state = 'running'  -- Only running instances
GROUP BY instance_type
ORDER BY total_cost DESC
LIMIT 10
```

### 5. Save Useful Queries

Keep a library of your most-used queries for quick access.

## Troubleshooting

### Query Returns No Results

**Problem:** Empty result set

**Solutions:**
1. Check your WHERE conditions
2. Verify column names (case-sensitive)
3. Use `SELECT DISTINCT column_name` to see available values
4. Remove filters one by one to isolate issue

### Column Not Found Error

**Problem:** "Column 'xyz' does not exist"

**Solutions:**
1. Check exact column name in data preview
2. Column names are case-sensitive
3. Use quotes for special characters: `"column-name"`
4. List all columns: `SELECT * FROM aws_data LIMIT 1`

### Syntax Error

**Problem:** SQL syntax error

**Solutions:**
1. Check for missing commas
2. Verify parentheses are balanced
3. Ensure proper quote usage (single quotes for strings)
4. Use example queries as templates

### Performance Issues

**Problem:** Query takes too long

**Solutions:**
1. Add LIMIT clause
2. Filter early with WHERE
3. Reduce number of JOINs
4. Use specific columns instead of SELECT *

## Advanced Features

### Window Functions

Calculate running totals:
```sql
SELECT 
    date,
    service,
    cost,
    SUM(cost) OVER (PARTITION BY service ORDER BY date) as running_total
FROM aws_data
ORDER BY service, date
```

### Subqueries

Compare to averages:
```sql
SELECT 
    service,
    cost,
    (SELECT AVG(cost) FROM aws_data) as overall_avg
FROM aws_data
WHERE cost > (SELECT AVG(cost) FROM aws_data)
```

### CTEs (Common Table Expressions)

Break complex queries into steps:
```sql
WITH monthly_costs AS (
    SELECT 
        DATE_TRUNC('month', date) as month,
        service,
        SUM(cost) as monthly_cost
    FROM aws_data
    GROUP BY month, service
)
SELECT 
    service,
    AVG(monthly_cost) as avg_monthly_cost,
    MAX(monthly_cost) as peak_monthly_cost
FROM monthly_costs
GROUP BY service
ORDER BY avg_monthly_cost DESC
```

## Integration with Chat

You can also ask the agent to generate SQL:

**User:** "Generate SQL to find my top 5 EC2 costs"

**Agent:** Generates and executes:
```sql
SELECT 
    instance_id,
    instance_type,
    SUM(cost) as total_cost
FROM aws_data
WHERE service = 'Amazon EC2'
GROUP BY instance_id, instance_type
ORDER BY total_cost DESC
LIMIT 5
```

## Summary

The SQL Query Examples feature provides:

✅ **Learning Tool** - Learn SQL by example
✅ **Time Saver** - Pre-built queries for common tasks
✅ **Customizable** - Easy to modify for your needs
✅ **Interactive** - Copy, execute, visualize in one place
✅ **Context-Aware** - Tailored to your specific data
✅ **Safe** - Dangerous operations blocked
✅ **Powerful** - Full SQL capabilities for precise analysis

Use example queries to unlock the full power of SQL-based analysis and gain deeper insights into your AWS costs!

---

**Master SQL, Master Your AWS Costs** 📊
