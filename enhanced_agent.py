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
