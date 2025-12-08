"""
Enhanced Intelligent AWS Agent with DuckDB and Text-to-SQL
Implements scalable analysis with SQL generation for accurate calculations
"""

import duckdb
import pandas as pd
import json
import re
from datetime import datetime
from intelligent_agent import IntelligentAWSAgent

class EnhancedAWSAgent(IntelligentAWSAgent):
    """
    Enhanced agent with DuckDB for scalability and Text-to-SQL for accuracy
    """
    
    def __init__(self):
        super().__init__()
        self.con = duckdb.connect(database=':memory:')
        self.table_name = 'aws_data'
        self.file_path = None
        
    def load_data_from_file(self, file_path):
        """
        Load data using DuckDB for scalability (handles large files)
        """
        try:
            self.file_path = file_path
            
            # Create table from CSV using DuckDB (zero-copy, handles large files)
            self.con.execute(f"""
                CREATE OR REPLACE TABLE {self.table_name} AS 
                SELECT * FROM read_csv_auto('{file_path}')
            """)
            
            # Get sample for analysis
            sample_df = self.con.execute(f"SELECT * FROM {self.table_name} LIMIT 1000").df()
            
            # Use parent class analysis on sample
            self.analyze_data(sample_df)
            
            # Store full data reference
            self.data = sample_df  # Keep sample for compatibility
            
            return True
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
    
    def generate_athena_query_from_prompt(self, user_prompt, is_cur_data=False):
        """
        Generate Athena SQL query based on user's natural language prompt
        Optimized for CUR (Cost & Usage Report) data structure
        """
        # Detect if this is CUR data
        columns = [col.lower() for col in self.data.columns]
        is_cur = is_cur_data or any('line_item' in col for col in columns)
        
        # Build column context
        if is_cur:
            # CUR-specific columns
            common_cur_columns = """
            Common CUR Columns:
            - line_item_usage_account_id: AWS Account ID
            - line_item_product_code: AWS Service (e.g., AmazonEC2, AmazonS3)
            - line_item_usage_type: Usage type details
            - line_item_operation: Operation performed
            - line_item_resource_id: Resource identifier
            - line_item_usage_start_date: Usage start timestamp
            - line_item_usage_end_date: Usage end timestamp
            - line_item_unblended_cost: Actual cost
            - line_item_blended_cost: Blended cost
            - product_region: AWS Region
            - product_instance_type: Instance type (for EC2)
            - resource_tags_*: Resource tags
            """
            table_name = "cost_and_usage_report"
        else:
            # Use actual columns from data
            columns_info = "\n".join([f"- {col}" for col in self.data.columns[:20]])
            common_cur_columns = f"Available Columns:\n{columns_info}"
            table_name = "your_table_name"
        
        query_template = f"""Generate an AWS Athena SQL query for the following request.

{common_cur_columns}

TABLE NAME: {table_name}

USER REQUEST: {user_prompt}

REQUIREMENTS:
1. Use Athena SQL syntax (Presto-based)
2. Include appropriate WHERE clauses for date filtering
3. Use proper aggregations (SUM, COUNT, AVG)
4. Add GROUP BY for dimensional analysis
5. Include ORDER BY for top results
6. Add LIMIT for large result sets
7. Use meaningful column aliases
8. Add comments explaining the query

Generate ONLY the SQL query with comments. No explanations before or after.

SQL Query:"""
        
        return query_template

    
    def execute_sql(self, sql_query):
        """
        Execute SQL query using DuckDB
        """
        try:
            # Sanitize SQL to prevent dangerous operations
            sanitized_sql = self._sanitize_sql(sql_query)
            
            result = self.con.execute(sanitized_sql).df()
            return result, None
        except Exception as e:
            return None, str(e)
    
    def _sanitize_sql(self, sql):
        """
        Sanitize SQL to prevent dangerous operations
        """
        # Convert to uppercase for checking
        sql_upper = sql.upper()
        
        # Block dangerous operations
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                raise ValueError(f"Dangerous SQL operation '{keyword}' not allowed")
        
        # Ensure query uses our table
        if self.table_name not in sql.lower() and 'aws_data' not in sql.lower():
            sql = sql.replace('FROM ', f'FROM {self.table_name} ')
        
        return sql

    
    def generate_sql_for_query(self, user_query):
        """
        Generate SQL query based on user's natural language question
        """
        # Build context about available columns and their types
        columns_info = []
        for col, dtype in self.data_profile['data_types'].items():
            columns_info.append(f"- {col} ({dtype})")
        
        columns_str = "\n".join(columns_info)
        
        prompt = f"""Generate a SQL query to answer the user's question.

TABLE: {self.table_name}
COLUMNS:
{columns_str}

COLUMN CLASSIFICATIONS:
- Cost columns: {', '.join(self.column_types['costs'])}
- Metric columns: {', '.join(self.column_types['metrics'][:5])}
- Dimension columns: {', '.join(self.column_types['dimensions'][:5])}

USER QUESTION: {user_query}

Generate ONLY the SQL query (SELECT statement). No explanations.
Use proper SQL syntax for DuckDB.
Only use SELECT statements (no DROP, DELETE, etc.).

SQL Query:"""

        return prompt

    
    def generate_aws_cli_commands(self, analysis_results):
        """
        Generate actionable AWS CLI commands based on analysis
        """
        commands = []
        
        # Example: Generate commands for unused resources
        if 'unused' in str(analysis_results).lower():
            commands.append({
                'action': 'Delete unused EBS volumes',
                'command': 'aws ec2 describe-volumes --filters "Name=status,Values=available" --query "Volumes[*].VolumeId" --output text | xargs -n 1 aws ec2 delete-volume --volume-id',
                'description': 'Removes unattached EBS volumes to save costs',
                'risk': 'MEDIUM - Ensure volumes are truly unused'
            })
        
        # Example: GP2 to GP3 migration
        if 'gp2' in str(analysis_results).lower():
            commands.append({
                'action': 'Migrate GP2 to GP3 volumes',
                'command': 'aws ec2 modify-volume --volume-id vol-xxxxx --volume-type gp3',
                'description': 'Upgrade to GP3 for better performance and lower cost',
                'risk': 'LOW - No downtime required'
            })
        
        # Example: Stop idle instances
        if 'idle' in str(analysis_results).lower() or 'underutilized' in str(analysis_results).lower():
            commands.append({
                'action': 'Stop idle EC2 instances',
                'command': 'aws ec2 stop-instances --instance-ids i-xxxxx',
                'description': 'Stop instances with low CPU utilization',
                'risk': 'MEDIUM - Verify instances are not needed'
            })
        
        return commands

    
    def generate_example_sql_queries(self, user_context=None):
        """
        Generate example SQL queries based on data structure and user context
        """
        examples = []
        
        # Get column information
        cost_cols = self.column_types.get('costs', [])
        metric_cols = self.column_types.get('metrics', [])
        dimension_cols = self.column_types.get('dimensions', [])
        date_cols = self.column_types.get('dates', [])
        
        # Basic queries
        examples.append({
            'category': 'Basic Analysis',
            'description': 'View sample data',
            'sql': f'SELECT * FROM {self.table_name} LIMIT 10',
            'use_case': 'Quick preview of your data'
        })
        
        examples.append({
            'category': 'Basic Analysis',
            'description': 'Count total rows',
            'sql': f'SELECT COUNT(*) as total_rows FROM {self.table_name}',
            'use_case': 'Understand data volume'
        })
        
        # Cost analysis queries
        if cost_cols:
            cost_col = cost_cols[0]
            
            examples.append({
                'category': 'Cost Analysis',
                'description': 'Total cost summary',
                'sql': f'''SELECT 
    SUM({cost_col}) as total_cost,
    AVG({cost_col}) as avg_cost,
    MAX({cost_col}) as max_cost,
    MIN({cost_col}) as min_cost
FROM {self.table_name}''',
                'use_case': 'Get overall cost statistics'
            })
            
            if dimension_cols:
                dim_col = dimension_cols[0]
                examples.append({
                    'category': 'Cost Analysis',
                    'description': f'Top 10 costs by {dim_col}',
                    'sql': f'''SELECT 
    {dim_col},
    SUM({cost_col}) as total_cost,
    COUNT(*) as count
FROM {self.table_name}
GROUP BY {dim_col}
ORDER BY total_cost DESC
LIMIT 10''',
                    'use_case': f'Identify highest cost {dim_col}s'
                })
                
                if len(dimension_cols) > 1:
                    dim_col2 = dimension_cols[1]
                    examples.append({
                        'category': 'Cost Analysis',
                        'description': f'Cost breakdown by {dim_col} and {dim_col2}',
                        'sql': f'''SELECT 
    {dim_col},
    {dim_col2},
    SUM({cost_col}) as total_cost
FROM {self.table_name}
GROUP BY {dim_col}, {dim_col2}
ORDER BY total_cost DESC
LIMIT 20''',
                        'use_case': f'Multi-dimensional cost analysis'
                    })
        
        # Date-based queries
        if date_cols and cost_cols:
            date_col = date_cols[0]
            cost_col = cost_cols[0]
            
            examples.append({
                'category': 'Trend Analysis',
                'description': 'Daily cost trends',
                'sql': f'''SELECT 
    {date_col},
    SUM({cost_col}) as daily_cost,
    COUNT(*) as records
FROM {self.table_name}
GROUP BY {date_col}
ORDER BY {date_col}''',
                'use_case': 'Track cost changes over time'
            })
            
            if dimension_cols:
                dim_col = dimension_cols[0]
                examples.append({
                    'category': 'Trend Analysis',
                    'description': f'Cost trends by {dim_col}',
                    'sql': f'''SELECT 
    {date_col},
    {dim_col},
    SUM({cost_col}) as cost
FROM {self.table_name}
GROUP BY {date_col}, {dim_col}
ORDER BY {date_col}, cost DESC''',
                    'use_case': f'Track {dim_col} costs over time'
                })
        
        # Optimization queries
        if 'state' in [col.lower() for col in self.data.columns]:
            examples.append({
                'category': 'Optimization',
                'description': 'Find unattached/unused resources',
                'sql': f'''SELECT 
    *
FROM {self.table_name}
WHERE LOWER(state) IN ('available', 'unused', 'stopped')''',
                'use_case': 'Identify resources that can be deleted'
            })
        
        if cost_cols and dimension_cols:
            cost_col = cost_cols[0]
            dim_col = dimension_cols[0]
            examples.append({
                'category': 'Optimization',
                'description': 'Resources with zero or minimal cost',
                'sql': f'''SELECT 
    {dim_col},
    {cost_col}
FROM {self.table_name}
WHERE {cost_col} < 1
ORDER BY {cost_col}''',
                'use_case': 'Find low-value resources'
            })
        
        # Aggregation queries
        if metric_cols and dimension_cols:
            metric_col = metric_cols[0]
            dim_col = dimension_cols[0]
            
            examples.append({
                'category': 'Metrics Analysis',
                'description': f'Average {metric_col} by {dim_col}',
                'sql': f'''SELECT 
    {dim_col},
    AVG({metric_col}) as avg_metric,
    MAX({metric_col}) as max_metric,
    MIN({metric_col}) as min_metric
FROM {self.table_name}
GROUP BY {dim_col}
ORDER BY avg_metric DESC''',
                'use_case': f'Analyze {metric_col} distribution'
            })
        
        # Filtering queries
        if dimension_cols:
            dim_col = dimension_cols[0]
            examples.append({
                'category': 'Filtering',
                'description': f'Filter by specific {dim_col}',
                'sql': f'''SELECT 
    *
FROM {self.table_name}
WHERE {dim_col} = 'YOUR_VALUE_HERE'
LIMIT 100''',
                'use_case': f'Focus on specific {dim_col}'
            })
        
        # Advanced queries
        if cost_cols and dimension_cols:
            cost_col = cost_cols[0]
            dim_col = dimension_cols[0]
            
            examples.append({
                'category': 'Advanced',
                'description': 'Cost distribution percentiles',
                'sql': f'''SELECT 
    {dim_col},
    SUM({cost_col}) as total_cost,
    ROUND(100.0 * SUM({cost_col}) / SUM(SUM({cost_col})) OVER (), 2) as cost_percentage
FROM {self.table_name}
GROUP BY {dim_col}
ORDER BY total_cost DESC''',
                'use_case': 'Understand cost distribution'
            })
            
            examples.append({
                'category': 'Advanced',
                'description': 'Resources above average cost',
                'sql': f'''SELECT 
    *
FROM {self.table_name}
WHERE {cost_col} > (SELECT AVG({cost_col}) FROM {self.table_name})
ORDER BY {cost_col} DESC''',
                'use_case': 'Find expensive outliers'
            })
        
        # Service-specific queries based on detected service
        if self.service:
            if 'EC2' in self.service or 'EBS' in self.service:
                examples.append({
                    'category': 'EC2/EBS Specific',
                    'description': 'Group by volume/instance type',
                    'sql': f'''SELECT 
    volume_type,
    COUNT(*) as count,
    SUM(size_gb) as total_size_gb
FROM {self.table_name}
GROUP BY volume_type
ORDER BY count DESC''',
                    'use_case': 'Analyze volume type distribution'
                })
            
            if 'S3' in self.service:
                examples.append({
                    'category': 'S3 Specific',
                    'description': 'Buckets by storage class',
                    'sql': f'''SELECT 
    storage_class,
    COUNT(*) as bucket_count,
    SUM(size_gb) as total_size_gb
FROM {self.table_name}
GROUP BY storage_class
ORDER BY total_size_gb DESC''',
                    'use_case': 'Analyze storage class usage'
                })
        
        return examples
    
    def get_table_stats(self):
        """
        Get table statistics using SQL (fast, accurate)
        """
        try:
            stats = {}
            
            # Total rows
            result = self.con.execute(f"SELECT COUNT(*) as count FROM {self.table_name}").fetchone()
            stats['total_rows'] = result[0]
            
            # Cost statistics if cost columns exist
            if self.column_types['costs']:
                cost_col = self.column_types['costs'][0]
                result = self.con.execute(f"""
                    SELECT 
                        SUM({cost_col}) as total_cost,
                        AVG({cost_col}) as avg_cost,
                        MAX({cost_col}) as max_cost,
                        MIN({cost_col}) as min_cost
                    FROM {self.table_name}
                """).fetchone()
                
                stats['total_cost'] = result[0] or 0
                stats['avg_cost'] = result[1] or 0
                stats['max_cost'] = result[2] or 0
                stats['min_cost'] = result[3] or 0
            
            # Top dimensions
            for dim in self.column_types['dimensions'][:3]:
                result = self.con.execute(f"""
                    SELECT {dim}, COUNT(*) as count
                    FROM {self.table_name}
                    GROUP BY {dim}
                    ORDER BY count DESC
                    LIMIT 5
                """).df()
                stats[f'top_{dim}'] = result.to_dict('records')
            
            return stats
        except Exception as e:
            return {}

    
    def perform_smart_aggregation(self, user_query):
        """
        Perform aggregation based on user query using SQL
        """
        # Detect aggregation type from query
        query_lower = user_query.lower()
        
        sql_queries = []
        
        # Top cost drivers
        if 'top' in query_lower and 'cost' in query_lower:
            if self.column_types['costs'] and self.column_types['dimensions']:
                cost_col = self.column_types['costs'][0]
                dim_col = self.column_types['dimensions'][0]
                
                sql = f"""
                    SELECT {dim_col}, SUM({cost_col}) as total_cost
                    FROM {self.table_name}
                    GROUP BY {dim_col}
                    ORDER BY total_cost DESC
                    LIMIT 10
                """
                sql_queries.append(('Top Cost Drivers', sql))
        
        # Average metrics
        if 'average' in query_lower or 'avg' in query_lower:
            if self.column_types['metrics']:
                metric_col = self.column_types['metrics'][0]
                if self.column_types['dimensions']:
                    dim_col = self.column_types['dimensions'][0]
                    sql = f"""
                        SELECT {dim_col}, AVG({metric_col}) as avg_metric
                        FROM {self.table_name}
                        GROUP BY {dim_col}
                        ORDER BY avg_metric DESC
                        LIMIT 10
                    """
                    sql_queries.append((f'Average {metric_col}', sql))
        
        # Execute queries
        results = {}
        for name, sql in sql_queries:
            df, error = self.execute_sql(sql)
            if df is not None:
                results[name] = df
        
        return results
    
    def close(self):
        """Close DuckDB connection"""
        if self.con:
            self.con.close()
