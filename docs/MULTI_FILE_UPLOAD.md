# Multi-File Upload & Intelligent Detection

## Overview

The FinOps GenAI Agent now supports uploading multiple CSV files simultaneously with intelligent auto-detection of file types. The agent can identify various AWS data sources and either analyze them individually or merge them for comprehensive analysis.

## Supported File Types

### AWS Native Exports

1. **Cost & Usage Report (CUR)**
   - Most comprehensive billing data
   - Line-item details for all AWS services
   - Detected by: `line_item_usage_account_id`, `line_item_product_code`, `line_item_unblended_cost`

2. **AWS Trusted Advisor**
   - Cost optimization recommendations
   - Security findings
   - Performance improvements
   - Detected by: `check_name`, `check_id`, `status`, `resource_id`

3. **Cost Optimization Hub**
   - Consolidated optimization recommendations
   - Estimated savings
   - Implementation effort
   - Detected by: `recommendation_id`, `estimated_monthly_savings`, `implementation_effort`

4. **AWS Compute Optimizer**
   - EC2 rightsizing recommendations
   - Instance type suggestions
   - Performance risk assessment
   - Detected by: `instance_arn`, `finding`, `current_instance_type`, `recommended_instance_type`

5. **Cost Explorer Exports**
   - Custom cost reports
   - Time-series cost data
   - Service breakdowns
   - Detected by: `time_period`, `service`, `amount`

### AWS Service Data

6. **EC2 Instances**
   - Instance inventory
   - Instance types and states
   - Detected by: `instance_id`, `instance_type`, `instance_state`

7. **EBS Volumes**
   - Volume inventory
   - Attached/unattached status
   - Volume types and sizes
   - Detected by: `volume_id`, `volume_type`, `state`

8. **S3 Buckets**
   - Bucket inventory
   - Storage classes
   - Access patterns
   - Detected by: `bucket_name`, `storage_class`

9. **RDS Instances**
   - Database inventory
   - Engine types
   - Instance classes
   - Detected by: `db_instance_identifier`, `db_instance_class`, `engine`

10. **Lambda Functions**
    - Function inventory
    - Runtime and memory
    - Invocation metrics
    - Detected by: `function_name`, `runtime`, `memory_size`

### Other Data Sources

11. **CloudWatch Metrics**
    - Performance metrics
    - Custom metrics
    - Time-series data
    - Detected by: `metric_name`, `namespace`, `timestamp`

12. **Savings Plans**
    - Commitment details
    - Utilization rates
    - Coverage metrics
    - Detected by: `savings_plan_arn`, `commitment`, `utilization`

13. **Reserved Instances**
    - Reservation details
    - Utilization tracking
    - Coverage analysis
    - Detected by: `reservation_id`, `instance_count`, `offering_type`

14. **Custom Script Outputs**
    - Any CSV with AWS data
    - Cost analysis results
    - Custom reports
    - Detected by: Column patterns and filename

## How It Works

### 1. Upload Multiple Files

```
📁 Upload Section
├── Click "Browse files"
├── Select multiple CSV files (Ctrl/Cmd + Click)
├── Or drag & drop multiple files
└── Agent processes all files
```

### 2. Automatic Detection

The agent analyzes each file:
- ✅ Examines column names
- ✅ Checks filename patterns
- ✅ Identifies data structure
- ✅ Determines file type
- ✅ Displays detection results

**Example Detection:**
```
📁 Uploaded Files Detection
├── cur_export_2024.csv          🔍 Detected: AWS Cost & Usage Report (CUR)
├── trusted_advisor.csv          🔍 Detected: AWS Trusted Advisor Report
└── ebs_volumes.csv              🔍 Detected: EBS Volumes Data
```

### 3. Analysis Options

**Single File:**
- Automatically analyzed
- Full feature set available

**Multiple Files:**
- Choose individual file to analyze
- Or merge compatible files
- Agent suggests best approach

## Usage Examples

### Example 1: CUR + Trusted Advisor

**Scenario:** Combine billing data with optimization recommendations

**Files:**
- `cur_december_2024.csv` - Cost & Usage Report
- `trusted_advisor_recommendations.csv` - TA recommendations

**Workflow:**
1. Upload both files
2. Agent detects both types
3. Choose "Analyze individually" or "Merge"
4. Ask: "Show me Trusted Advisor recommendations for my highest cost services"

**Benefits:**
- Cross-reference costs with recommendations
- Prioritize optimizations by cost impact
- Validate TA findings against actual usage

### Example 2: Multiple Monthly CUR Files

**Scenario:** Analyze cost trends across multiple months

**Files:**
- `cur_october_2024.csv`
- `cur_november_2024.csv`
- `cur_december_2024.csv`

**Workflow:**
1. Upload all three files
2. Agent detects all as CUR
3. Select "Merge all files"
4. Ask: "Show me month-over-month cost trends"

**Benefits:**
- Comprehensive trend analysis
- Identify seasonal patterns
- Track cost growth over time

### Example 3: Cost Optimization Hub + Compute Optimizer

**Scenario:** Comprehensive optimization analysis

**Files:**
- `cost_optimization_hub.csv` - All recommendations
- `compute_optimizer_ec2.csv` - EC2 rightsizing

**Workflow:**
1. Upload both files
2. Agent detects both types
3. Analyze individually or merge
4. Ask: "What are my top 10 optimization opportunities by savings?"

**Benefits:**
- Consolidated view of all recommendations
- Compare different optimization types
- Prioritize by ROI

### Example 4: EBS + S3 + EC2 Inventory

**Scenario:** Complete resource inventory analysis

**Files:**
- `ebs_volumes.csv` - All EBS volumes
- `s3_buckets.csv` - All S3 buckets
- `ec2_instances.csv` - All EC2 instances

**Workflow:**
1. Upload all three files
2. Agent detects all resource types
3. Analyze individually or merge
4. Ask: "Show me total storage costs across EBS and S3"

**Benefits:**
- Holistic resource view
- Cross-service analysis
- Identify optimization opportunities

### Example 5: Custom Script Output + CUR

**Scenario:** Validate custom analysis against billing data

**Files:**
- `my_cost_analysis.csv` - Custom script output
- `cur_current_month.csv` - Official CUR data

**Workflow:**
1. Upload both files
2. Agent detects types
3. Compare results
4. Ask: "Validate my custom analysis against CUR data"

**Benefits:**
- Verify custom calculations
- Find discrepancies
- Improve custom scripts

## Merging Strategies

The agent uses intelligent merging strategies:

### Strategy 1: Identical Columns
**When:** All files have the same columns
**Action:** Simple vertical concatenation
**Example:** Multiple monthly CUR files

```python
# All files have: date, service, cost, region
Result: Combined dataset with all rows
```

### Strategy 2: Common Columns
**When:** Files have overlapping columns (3+)
**Action:** Merge on common columns only
**Example:** Different AWS service exports

```python
# File 1: date, service, cost, instance_id
# File 2: date, service, cost, volume_id
Common: date, service, cost
Result: Combined dataset with common columns
```

### Strategy 3: Key-Based Join
**When:** Files share key columns
**Action:** Join on key columns (date, service, region, etc.)
**Example:** CUR + Trusted Advisor

```python
# Join on: date, service, region
Result: Enriched dataset with both sources
```

### Strategy 4: Incompatible Files
**When:** No common structure
**Action:** Analyze individually
**Example:** CUR + CloudWatch metrics

```
❌ Files cannot be merged
✅ Analyze each file separately
```

## Best Practices

### File Naming

Use descriptive names:
- ✅ `cur_december_2024.csv`
- ✅ `trusted_advisor_cost_optimization.csv`
- ✅ `ebs_volumes_unattached.csv`
- ❌ `data.csv`
- ❌ `export.csv`

### File Organization

Group related files:
```
uploads/
├── billing/
│   ├── cur_oct_2024.csv
│   ├── cur_nov_2024.csv
│   └── cur_dec_2024.csv
├── optimization/
│   ├── trusted_advisor.csv
│   └── cost_optimization_hub.csv
└── inventory/
    ├── ec2_instances.csv
    ├── ebs_volumes.csv
    └── s3_buckets.csv
```

### Upload Order

Upload in logical order:
1. Primary data source (CUR)
2. Supplementary data (Trusted Advisor)
3. Inventory data (EC2, EBS, S3)

### File Size

- ✅ Single files: Up to 1GB (DuckDB handles efficiently)
- ✅ Multiple files: Total up to 2GB
- ⚠️ Very large files: Consider splitting by month/service

### Data Quality

Ensure clean data:
- ✅ Consistent date formats
- ✅ No missing headers
- ✅ Valid CSV format
- ✅ UTF-8 encoding

## Sample Questions for Multi-File Analysis

### Cross-File Analysis

**CUR + Trusted Advisor:**
- "Show me Trusted Advisor recommendations for services with highest costs"
- "What's the potential savings from implementing all TA recommendations?"
- "Which TA recommendations would have the biggest cost impact?"

**CUR + Cost Optimization Hub:**
- "Compare my actual costs with Cost Optimization Hub savings estimates"
- "Show me optimization recommendations by implementation effort"
- "What's my total optimization potential?"

**Multiple Monthly CUR:**
- "Show me month-over-month cost trends by service"
- "Which services have the highest cost growth?"
- "Forecast next month's costs based on trends"

**Inventory Files:**
- "Show me total storage costs across EBS and S3"
- "Which resources are unattached or unused?"
- "Calculate total potential savings from resource optimization"

### Individual File Analysis

**After uploading multiple files:**
- "Analyze the Trusted Advisor file"
- "Show me insights from the EBS volumes data"
- "What does the CUR data tell us about EC2 costs?"

## Troubleshooting

### Files Not Merging

**Problem:** "Files are not compatible for merging"

**Solutions:**
1. Check if files have common columns
2. Analyze files individually
3. Manually align columns before upload
4. Use key-based join if possible

### Wrong File Type Detected

**Problem:** Agent misidentifies file type

**Solutions:**
1. Rename file with descriptive name
2. Add identifying columns
3. Manually specify in chat: "This is a CUR file"
4. Check column names match AWS standards

### Large File Performance

**Problem:** Slow upload or processing

**Solutions:**
1. Split large files by time period
2. Filter to relevant columns before upload
3. Use DuckDB-compatible formats
4. Upload one file at a time

### Memory Issues

**Problem:** Out of memory errors

**Solutions:**
1. Reduce number of simultaneous files
2. Use smaller date ranges
3. Filter data before upload
4. Restart application

## Advanced Features

### Programmatic Detection

The agent uses sophisticated detection logic:

```python
def detect_file_type(df, filename):
    # Check columns
    columns = [col.lower() for col in df.columns]
    
    # Check filename
    filename_lower = filename.lower()
    
    # Pattern matching
    if 'line_item_usage_account_id' in columns:
        return "AWS Cost & Usage Report (CUR)"
    
    # ... more detection logic
```

### Custom Detection Rules

You can extend detection by:
1. Adding custom column patterns
2. Using filename conventions
3. Implementing custom logic

### Merge Validation

The agent validates merges:
- ✅ Checks column compatibility
- ✅ Validates data types
- ✅ Ensures no data loss
- ✅ Reports merge statistics

## API Reference

### File Upload

```python
uploaded_files = st.file_uploader(
    "Upload CSV file(s)",
    type=['csv'],
    accept_multiple_files=True
)
```

### Detection

```python
file_type = detect_file_type(df, filename)
# Returns: "AWS Cost & Usage Report (CUR)"
```

### Merging

```python
merged_df, success = merge_files(files_info)
# Returns: (DataFrame, bool)
```

## Summary

Multi-file upload with intelligent detection provides:

✅ **Flexibility** - Upload any combination of AWS data
✅ **Intelligence** - Auto-detect file types
✅ **Integration** - Merge compatible files
✅ **Analysis** - Cross-reference multiple sources
✅ **Efficiency** - Process multiple files at once
✅ **Insights** - Comprehensive view of AWS environment

Upload multiple files to unlock powerful cross-source analysis and get deeper insights into your AWS costs and optimization opportunities!

---

**Supported file types: 14+ AWS data sources and counting!** 📊
