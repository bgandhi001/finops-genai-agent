"""
Intelligent AWS Data Analysis Agent
Works with any AWS service SQL output, generates insights, and answers questions
"""

import pandas as pd
import json
from datetime import datetime
import re

class IntelligentAWSAgent:
    """
    Smart agent that can analyze any AWS service data and provide insights
    """
    
    def __init__(self):
        self.data = None
        self.data_profile = None
        self.aws_service = None
        self.column_types = {}
        
    def analyze_data(self, df):
        """
        Automatically analyze uploaded data and understand its structure
        """
        self.data = df
        self.data_profile = self._profile_data(df)
        self.aws_service = self._detect_aws_service(df)
        self.column_types = self._classify_columns(df)
        
        return {
            'service': self.aws_service,
            'profile': self.data_profile,
            'column_types': self.column_types
        }
    
    def _profile_data(self, df):
        """Create a comprehensive data profile"""
        profile = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': df.columns.tolist(),
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            'text_columns': df.select_dtypes(include=['object']).columns.tolist(),
            'date_columns': [],
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.astype(str).to_dict(),
            'sample_values': {}
        }
        
        # Detect date columns
        for col in df.columns:
            if any(date_word in col.lower() for date_word in ['date', 'time', 'timestamp', 'created', 'modified']):
                profile['date_columns'].append(col)
        
        # Get sample values for each column
        for col in df.columns:
            unique_count = df[col].nunique()
            if unique_count <= 10:
                profile['sample_values'][col] = df[col].unique().tolist()[:5]
            else:
                profile['sample_values'][col] = df[col].value_counts().head(3).index.tolist()
        
        return profile
    
    def _detect_aws_service(self, df):
        """
        Automatically detect which AWS service this data is from
        """
        columns_str = ' '.join(df.columns).lower()
        
        # Service detection patterns
        service_patterns = {
            'EC2': ['instance', 'ec2', 'availability_zone', 'instance_type', 'ami'],
            'S3': ['bucket', 's3', 'storage', 'object'],
            'RDS': ['rds', 'database', 'db_instance', 'engine'],
            'Lambda': ['lambda', 'function', 'invocation', 'duration'],
            'DynamoDB': ['dynamodb', 'table', 'read_capacity', 'write_capacity'],
            'CloudFront': ['cloudfront', 'distribution', 'edge'],
            'EBS': ['volume', 'ebs', 'snapshot', 'gp2', 'gp3'],
            'VPC': ['vpc', 'subnet', 'nat', 'gateway', 'endpoint'],
            'ELB': ['load_balancer', 'elb', 'alb', 'nlb', 'target'],
            'CloudWatch': ['metric', 'alarm', 'log', 'cloudwatch'],
            'Cost & Usage Report': ['line_item', 'usage_type', 'unblended_cost', 'blended_cost'],
            'IAM': ['user', 'role', 'policy', 'permission', 'iam'],
            'Route53': ['route53', 'dns', 'hosted_zone', 'record'],
            'SQS': ['queue', 'sqs', 'message'],
            'SNS': ['topic', 'sns', 'subscription'],
            'ECS': ['ecs', 'task', 'container', 'cluster', 'fargate'],
            'EKS': ['eks', 'kubernetes', 'node', 'pod'],
            'Athena': ['athena', 'query', 'execution'],
            'Glue': ['glue', 'crawler', 'job', 'catalog'],
            'Redshift': ['redshift', 'cluster', 'node', 'warehouse']
        }
        
        # Check for cost-related columns
        cost_columns = [col for col in df.columns if 'cost' in col.lower() or 'charge' in col.lower() or 'price' in col.lower()]
        if cost_columns:
            return 'Cost & Usage Report'
        
        # Match against patterns
        for service, patterns in service_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in columns_str)
            if matches >= 2:
                return service
        
        return 'Unknown AWS Service'
    
    def _classify_columns(self, df):
        """
        Classify columns by their purpose
        """
        classification = {
            'identifiers': [],
            'metrics': [],
            'dimensions': [],
            'timestamps': [],
            'costs': [],
            'tags': []
        }
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Identifiers
            if any(word in col_lower for word in ['id', 'arn', 'resource_id', 'account']):
                classification['identifiers'].append(col)
            
            # Metrics (numeric values)
            elif df[col].dtype in ['int64', 'float64']:
                if 'cost' in col_lower or 'charge' in col_lower or 'price' in col_lower:
                    classification['costs'].append(col)
                else:
                    classification['metrics'].append(col)
            
            # Timestamps
            elif any(word in col_lower for word in ['date', 'time', 'timestamp', 'created', 'modified']):
                classification['timestamps'].append(col)
            
            # Tags
            elif 'tag' in col_lower:
                classification['tags'].append(col)
            
            # Dimensions (categorical)
            else:
                classification['dimensions'].append(col)
        
        return classification
    
    def generate_smart_questions(self):
        """
        Generate contextual questions based on the data
        """
        if self.data is None:
            return []
        
        questions = []
        service = self.aws_service
        cols = self.column_types
        
        # Cost-related questions
        if cols['costs']:
            cost_col = cols['costs'][0]
            questions.extend([
                f"💰 What are the top 5 cost drivers in this {service} data?",
                f"📊 Show me a breakdown of {cost_col} by {cols['dimensions'][0] if cols['dimensions'] else 'category'}",
                f"📈 What's the total {cost_col} and how is it distributed?",
                f"🎯 Identify cost optimization opportunities in this data"
            ])
        
        # Time-series questions
        if cols['timestamps']:
            time_col = cols['timestamps'][0]
            questions.extend([
                f"📅 Show me trends over time using {time_col}",
                f"🔍 What patterns can you identify in the time series data?",
                f"📉 Are there any anomalies or spikes in the data?"
            ])
        
        # Service-specific questions
        if service == 'EC2':
            questions.extend([
                "🖥️ Which instance types are most used?",
                "🌍 Show me distribution across availability zones",
                "💡 Are there any underutilized instances?"
            ])
        elif service == 'S3':
            questions.extend([
                "🪣 Which buckets have the highest storage costs?",
                "📦 What's the total storage size?",
                "🔄 Identify opportunities for lifecycle policies"
            ])
        elif service == 'RDS':
            questions.extend([
                "🗄️ Which database instances are most expensive?",
                "⚡ Are there any performance optimization opportunities?",
                "💾 Show me storage utilization"
            ])
        elif service == 'Lambda':
            questions.extend([
                "⚡ Which functions have the highest invocation count?",
                "⏱️ What's the average execution duration?",
                "💰 Which functions are most expensive?"
            ])
        
        # Dimension-based questions
        if cols['dimensions']:
            dim = cols['dimensions'][0]
            questions.extend([
                f"📊 Group and analyze data by {dim}",
                f"🔝 What are the top values in {dim}?"
            ])
        
        # Metric-based questions
        if cols['metrics']:
            metric = cols['metrics'][0]
            questions.extend([
                f"📈 Show me statistics for {metric}",
                f"🎯 What's the distribution of {metric}?"
            ])
        
        # General questions
        questions.extend([
            "🔍 Summarize the key insights from this data",
            "📋 Create a prioritized action plan based on this data",
            "💡 What are the quick wins I can implement?",
            "📊 Generate a comprehensive report"
        ])
        
        return questions[:10]  # Return top 10 questions
    
    def generate_analysis_prompt(self, user_query):
        """
        Generate a comprehensive prompt for the LLM based on data understanding
        """
        context = {
            'service': self.aws_service,
            'data_profile': self.data_profile,
            'column_types': self.column_types,
            'sample_data': self.data.head(20).to_dict('records') if self.data is not None else []
        }
        
        prompt = f"""You are an expert AWS Solutions Architect and FinOps specialist analyzing {self.aws_service} data.

DATA CONTEXT:
- AWS Service: {self.aws_service}
- Total Records: {self.data_profile['total_rows']}
- Columns: {', '.join(self.data_profile['columns'])}

COLUMN CLASSIFICATION:
- Cost Columns: {', '.join(self.column_types['costs']) if self.column_types['costs'] else 'None'}
- Metric Columns: {', '.join(self.column_types['metrics'][:5]) if self.column_types['metrics'] else 'None'}
- Dimension Columns: {', '.join(self.column_types['dimensions'][:5]) if self.column_types['dimensions'] else 'None'}
- Time Columns: {', '.join(self.column_types['timestamps']) if self.column_types['timestamps'] else 'None'}

SAMPLE DATA:
{json.dumps(context['sample_data'][:5], indent=2)}

USER QUERY: {user_query}

INSTRUCTIONS:
1. Analyze the data in the context of {self.aws_service}
2. Provide specific, actionable insights
3. Include relevant metrics and calculations
4. Suggest AWS best practices
5. Identify cost optimization opportunities
6. Format your response in clear markdown with sections
7. Use emojis for better readability

Provide a comprehensive, data-driven response."""

        return prompt, context
    
    def create_summary_table(self):
        """
        Create a summary table based on data analysis
        """
        if self.data is None:
            return None
        
        summary = {}
        
        # Cost summary
        if self.column_types['costs']:
            for cost_col in self.column_types['costs']:
                summary[f'Total {cost_col}'] = f"${self.data[cost_col].sum():,.2f}"
                summary[f'Average {cost_col}'] = f"${self.data[cost_col].mean():,.2f}"
                summary[f'Max {cost_col}'] = f"${self.data[cost_col].max():,.2f}"
        
        # Metric summary
        for metric in self.column_types['metrics'][:3]:
            summary[f'Total {metric}'] = f"{self.data[metric].sum():,.0f}"
            summary[f'Average {metric}'] = f"{self.data[metric].mean():,.2f}"
        
        # Dimension summary
        for dim in self.column_types['dimensions'][:2]:
            unique_count = self.data[dim].nunique()
            summary[f'Unique {dim}'] = unique_count
            if unique_count <= 10:
                top_value = self.data[dim].value_counts().index[0]
                summary[f'Top {dim}'] = top_value
        
        return summary
    
    def get_aggregation_suggestions(self):
        """
        Suggest useful aggregations based on data structure
        """
        suggestions = []
        
        if not self.column_types['dimensions']:
            return suggestions
        
        # Cost aggregations
        if self.column_types['costs']:
            cost_col = self.column_types['costs'][0]
            for dim in self.column_types['dimensions'][:3]:
                suggestions.append({
                    'type': 'sum',
                    'metric': cost_col,
                    'group_by': dim,
                    'description': f"Total {cost_col} by {dim}"
                })
        
        # Metric aggregations
        for metric in self.column_types['metrics'][:2]:
            for dim in self.column_types['dimensions'][:2]:
                suggestions.append({
                    'type': 'mean',
                    'metric': metric,
                    'group_by': dim,
                    'description': f"Average {metric} by {dim}"
                })
        
        # Count aggregations
        for dim in self.column_types['dimensions'][:2]:
            suggestions.append({
                'type': 'count',
                'group_by': dim,
                'description': f"Count of records by {dim}"
            })
        
        return suggestions[:5]
    
    def perform_aggregation(self, agg_type, metric=None, group_by=None):
        """
        Perform aggregation on the data
        """
        if self.data is None or not group_by:
            return None
        
        try:
            if agg_type == 'sum' and metric:
                result = self.data.groupby(group_by)[metric].sum().sort_values(ascending=False)
            elif agg_type == 'mean' and metric:
                result = self.data.groupby(group_by)[metric].mean().sort_values(ascending=False)
            elif agg_type == 'count':
                result = self.data.groupby(group_by).size().sort_values(ascending=False)
            else:
                return None
            
            return result.head(10).to_dict()
        except Exception as e:
            return None
