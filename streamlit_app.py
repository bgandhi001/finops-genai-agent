import streamlit as st
import pandas as pd
import json
import boto3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import os
from pathlib import Path
from intelligent_agent import IntelligentAWSAgent
from enhanced_agent import EnhancedAWSAgent

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load .env on startup
load_env_file()

# AWS Bedrock client initialization
@st.cache_resource
def get_bedrock_client():
    return boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))

@st.cache_resource
def get_dynamodb_client():
    return boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))

# Initialize session state
def init_session_state():
    if 'session_id' not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.session_start = datetime.now()
        log_session_start()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None
    if 'data_summary' not in st.session_state:
        st.session_state.data_summary = None
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {}
    if 'query_count' not in st.session_state:
        st.session_state.query_count = 0
    if 'file_upload_count' not in st.session_state:
        st.session_state.file_upload_count = 0
    if 'intelligent_agent' not in st.session_state:
        # Use EnhancedAWSAgent for better performance and scalability
        st.session_state.intelligent_agent = EnhancedAWSAgent()
    if 'use_enhanced_agent' not in st.session_state:
        st.session_state.use_enhanced_agent = True

def detect_file_type(df, filename):
    """Intelligently detect the type of AWS data file"""
    columns = [col.lower() for col in df.columns]
    filename_lower = filename.lower()
    
    # Cost & Usage Report (CUR)
    if any(col in columns for col in ['line_item_usage_account_id', 'line_item_product_code', 'line_item_unblended_cost']):
        return "AWS Cost & Usage Report (CUR)"
    
    # Trusted Advisor
    if any(col in columns for col in ['check_name', 'check_id', 'status', 'resource_id']) or 'trusted' in filename_lower:
        return "AWS Trusted Advisor Report"
    
    # Cost Optimization Hub
    if any(col in columns for col in ['recommendation_id', 'estimated_monthly_savings', 'implementation_effort']) or 'optimization' in filename_lower:
        return "AWS Cost Optimization Hub Export"
    
    # Compute Optimizer
    if any(col in columns for col in ['instance_arn', 'finding', 'current_instance_type', 'recommended_instance_type']):
        return "AWS Compute Optimizer Report"
    
    # EBS Volumes
    if any(col in columns for col in ['volume_id', 'volume_type', 'state']) and 'volume' in filename_lower:
        return "EBS Volumes Data"
    
    # S3 Buckets
    if any(col in columns for col in ['bucket_name', 'storage_class']) or 'bucket' in filename_lower:
        return "S3 Buckets Data"
    
    # EC2 Instances
    if any(col in columns for col in ['instance_id', 'instance_type', 'instance_state']):
        return "EC2 Instances Data"
    
    # RDS Instances
    if any(col in columns for col in ['db_instance_identifier', 'db_instance_class', 'engine']):
        return "RDS Instances Data"
    
    # Lambda Functions
    if any(col in columns for col in ['function_name', 'runtime', 'memory_size']):
        return "Lambda Functions Data"
    
    # CloudWatch Metrics
    if any(col in columns for col in ['metric_name', 'namespace', 'timestamp']):
        return "CloudWatch Metrics Data"
    
    # Cost Explorer Export
    if any(col in columns for col in ['time_period', 'service', 'amount']):
        return "Cost Explorer Export"
    
    # Savings Plans
    if any(col in columns for col in ['savings_plan_arn', 'commitment', 'utilization']):
        return "Savings Plans Data"
    
    # Reserved Instances
    if any(col in columns for col in ['reservation_id', 'instance_count', 'offering_type']):
        return "Reserved Instances Data"
    
    # Generic AWS service data
    if 'service' in columns or 'aws' in filename_lower:
        return "AWS Service Data"
    
    # Monthly trends
    if 'month' in columns and 'cost' in columns:
        return "Monthly Cost Trends"
    
    # Generic cost data
    if any(col in columns for col in ['cost', 'charge', 'amount', 'price']):
        return "Cost Analysis Data"
    
    return "Unknown AWS Data"

def merge_files(files_info):
    """Attempt to merge multiple files intelligently"""
    try:
        # Check if all files have compatible structures
        first_file = files_info[0]
        first_columns = set(first_file['df'].columns)
        
        # Check for common columns
        common_columns = first_columns.copy()
        for file_info in files_info[1:]:
            common_columns &= set(file_info['df'].columns)
        
        if len(common_columns) == 0:
            # No common columns - can't merge
            return None, False
        
        # Strategy 1: All files have same columns - simple concatenation
        all_same_columns = all(
            set(f['df'].columns) == first_columns 
            for f in files_info
        )
        
        if all_same_columns:
            # Simple vertical concatenation
            merged_df = pd.concat([f['df'] for f in files_info], ignore_index=True)
            return merged_df, True
        
        # Strategy 2: Files have overlapping columns - merge on common columns
        if len(common_columns) >= 3:  # Need at least 3 common columns
            # Use only common columns
            dfs_with_common = [f['df'][list(common_columns)] for f in files_info]
            merged_df = pd.concat(dfs_with_common, ignore_index=True)
            return merged_df, True
        
        # Strategy 3: Try to join on key columns
        key_columns = ['date', 'service', 'region', 'resource_id', 'instance_id', 'volume_id', 'bucket_name']
        found_keys = [col for col in key_columns if col in common_columns]
        
        if found_keys:
            # Join on found keys
            merged_df = files_info[0]['df']
            for file_info in files_info[1:]:
                merged_df = pd.merge(
                    merged_df, 
                    file_info['df'], 
                    on=found_keys, 
                    how='outer',
                    suffixes=('', f'_{file_info["name"][:10]}')
                )
            return merged_df, True
        
        # Can't merge
        return None, False
        
    except Exception as e:
        st.error(f"Error merging files: {str(e)}")
        return None, False

def analyze_uploaded_data(df):
    """Analyze uploaded data using intelligent agent"""
    # Use intelligent agent for analysis
    agent = st.session_state.intelligent_agent
    analysis = agent.analyze_data(df)
    
    # Create summary compatible with existing code
    summary = {
        'total_rows': analysis['profile']['total_rows'],
        'total_columns': analysis['profile']['total_columns'],
        'columns': analysis['profile']['columns'],
        'numeric_columns': analysis['profile']['numeric_columns'],
        'total_cost': 0,
        'date_range': None,
        'aws_service': analysis['service'],
        'column_types': analysis['column_types'],
        'data_profile': analysis['profile']
    }
    
    # Calculate total cost if cost columns exist
    if analysis['column_types']['costs']:
        cost_col = analysis['column_types']['costs'][0]
        summary['total_cost'] = df[cost_col].sum()
    
    return summary

def generate_suggested_prompts(data_summary, analysis_type):
    """Generate contextual prompts using intelligent agent"""
    # Use intelligent agent to generate smart questions
    agent = st.session_state.intelligent_agent
    
    if agent.data is not None:
        smart_questions = agent.generate_smart_questions()
        if smart_questions:
            return smart_questions
    
    # Fallback to type-based prompts
    if analysis_type == "Architecture Inference":
        prompts = [
            "🔍 Analyze cross-AZ data transfer patterns and suggest optimizations",
            "💰 Identify the top 3 cost drivers and recommend architectural changes",
            "🏗️ What architectural inefficiencies can you detect from this data?",
            "📊 Show me a breakdown of costs by availability zone",
            "🎯 Calculate potential savings from implementing VPC endpoints"
        ]
    elif analysis_type == "Tagging Analysis":
        prompts = [
            "🏷️ Find untagged resources and suggest probable owners",
            "🔗 Show correlation between untagged and tagged resources",
            "📈 What's the total cost of untagged resources?",
            "🎲 Calculate confidence scores for tag recommendations",
            "📋 Generate a tagging remediation plan"
        ]
    else:
        prompts = [
            "📊 Summarize the key insights from this data",
            "💡 What are the top optimization opportunities?",
            "📉 Show me cost trends and anomalies",
            "🎯 Create a prioritized action plan"
        ]
    
    return prompts

def make_json_serializable(obj):
    """Convert non-JSON-serializable objects to serializable format"""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    elif pd.isna(obj):
        return None
    elif hasattr(obj, 'item'):  # numpy types
        return obj.item()
    else:
        return obj

def call_bedrock_llm(prompt, context_data, chat_history):
    """Call AWS Bedrock with Claude for analysis using intelligent agent"""
    try:
        bedrock = get_bedrock_client()
        
        # Make context data JSON serializable
        context_data = make_json_serializable(context_data)
        
        # Use intelligent agent to generate enhanced prompt
        agent = st.session_state.intelligent_agent
        if agent.data is not None:
            enhanced_prompt, enhanced_context = agent.generate_analysis_prompt(prompt)
        else:
            # Fallback to basic prompt
            conversation_context = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                for msg in chat_history[-5:]
            ])
            
            enhanced_prompt = f"""You are an expert FinOps Architect Assistant with deep knowledge of AWS cost optimization.

Context Data:
{json.dumps(context_data, indent=2)}

Previous Conversation:
{conversation_context}

User Query: {prompt}

Provide detailed, actionable insights with:
1. Clear analysis of the data
2. Specific recommendations
3. Estimated cost savings where applicable
4. Implementation steps

Format your response in markdown with clear sections."""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": enhanced_prompt
                }
            ],
            "temperature": 0.7
        })
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=body
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    except Exception as e:
        return f"⚠️ Error calling Bedrock: {str(e)}\n\nPlease ensure AWS credentials are configured and Bedrock is enabled."

def log_session_start():
    """Log session start event"""
    try:
        dynamodb = get_dynamodb_client()
        table_name = os.getenv('DYNAMODB_TABLE', 'finops-agent-interactions')
        table = dynamodb.Table(table_name)
        
        item = {
            'interaction_id': f"session_{st.session_state.session_id}",
            'timestamp': datetime.now().isoformat(),
            'event_type': 'session_start',
            'session_id': st.session_state.session_id,
            'session_start': st.session_state.session_start.isoformat(),
            'user_agent': 'streamlit_app',
            'ttl': int((datetime.now().timestamp() + 90*24*60*60))  # 90 days retention
        }
        
        table.put_item(Item=item)
    except Exception as e:
        pass  # Silent fail for logging

def log_file_upload(file_info):
    """Log file upload event"""
    try:
        dynamodb = get_dynamodb_client()
        table_name = os.getenv('DYNAMODB_TABLE', 'finops-agent-interactions')
        table = dynamodb.Table(table_name)
        
        st.session_state.file_upload_count += 1
        
        item = {
            'interaction_id': f"upload_{st.session_state.session_id}_{st.session_state.file_upload_count}",
            'timestamp': datetime.now().isoformat(),
            'event_type': 'file_upload',
            'session_id': st.session_state.session_id,
            'file_name': file_info.get('name', 'unknown'),
            'file_size': file_info.get('size', 0),
            'row_count': file_info.get('rows', 0),
            'column_count': file_info.get('columns', 0),
            'analysis_type': file_info.get('analysis_type', 'unknown'),
            'ttl': int((datetime.now().timestamp() + 90*24*60*60))
        }
        
        table.put_item(Item=item)
    except Exception as e:
        pass

def log_user_query(user_query, query_metadata):
    """Log user query event"""
    try:
        dynamodb = get_dynamodb_client()
        table_name = os.getenv('DYNAMODB_TABLE', 'finops-agent-interactions')
        table = dynamodb.Table(table_name)
        
        st.session_state.query_count += 1
        
        item = {
            'interaction_id': f"query_{st.session_state.session_id}_{st.session_state.query_count}",
            'timestamp': datetime.now().isoformat(),
            'event_type': 'user_query',
            'session_id': st.session_state.session_id,
            'user_query': user_query,
            'query_length': len(user_query),
            'is_suggested_prompt': query_metadata.get('is_suggested', False),
            'analysis_type': query_metadata.get('analysis_type', 'unknown'),
            'has_data': query_metadata.get('has_data', False),
            'ttl': int((datetime.now().timestamp() + 90*24*60*60))
        }
        
        table.put_item(Item=item)
    except Exception as e:
        pass

def log_agent_response(user_query, agent_response, response_metadata):
    """Log agent response with analytics"""
    try:
        dynamodb = get_dynamodb_client()
        table_name = os.getenv('DYNAMODB_TABLE', 'finops-agent-interactions')
        table = dynamodb.Table(table_name)
        
        item = {
            'interaction_id': f"response_{st.session_state.session_id}_{st.session_state.query_count}",
            'timestamp': datetime.now().isoformat(),
            'event_type': 'agent_response',
            'session_id': st.session_state.session_id,
            'user_query': user_query,
            'agent_response': agent_response[:1000],  # Truncate for storage
            'response_length': len(agent_response),
            'processing_time': response_metadata.get('processing_time', 0),
            'has_visualization': response_metadata.get('has_visualization', False),
            'analysis_type': response_metadata.get('analysis_type', 'unknown'),
            'data_summary': json.dumps(response_metadata.get('data_summary', {})),
            'ttl': int((datetime.now().timestamp() + 90*24*60*60))
        }
        
        table.put_item(Item=item)
    except Exception as e:
        pass

def log_session_end():
    """Log session end event with summary"""
    try:
        dynamodb = get_dynamodb_client()
        table_name = os.getenv('DYNAMODB_TABLE', 'finops-agent-interactions')
        table = dynamodb.Table(table_name)
        
        session_duration = (datetime.now() - st.session_state.session_start).total_seconds()
        
        item = {
            'interaction_id': f"session_end_{st.session_state.session_id}",
            'timestamp': datetime.now().isoformat(),
            'event_type': 'session_end',
            'session_id': st.session_state.session_id,
            'session_duration': session_duration,
            'total_queries': st.session_state.query_count,
            'total_uploads': st.session_state.file_upload_count,
            'chat_messages': len(st.session_state.chat_history),
            'ttl': int((datetime.now().timestamp() + 90*24*60*60))
        }
        
        table.put_item(Item=item)
    except Exception as e:
        pass

def save_interaction_to_dynamodb(user_query, agent_response, data_context):
    """Save user interactions for learning (legacy function - now uses detailed logging)"""
    # This function is kept for backward compatibility
    # New code should use log_agent_response instead
    pass

def create_cost_visualization(df, chart_type="bar"):
    """Generate visualizations based on data"""
    if df is None or df.empty:
        return None
    
    # Detect cost and grouping columns
    cost_col = next((col for col in df.columns if 'cost' in col.lower()), None)
    
    if not cost_col:
        return None
    
    if chart_type == "bar":
        # Group by first non-cost column
        group_col = [col for col in df.columns if col != cost_col][0]
        grouped = df.groupby(group_col)[cost_col].sum().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=grouped.index,
            y=grouped.values,
            labels={'x': group_col, 'y': f'Total Cost ($)'},
            title=f'Top 10 Cost Drivers by {group_col}'
        )
        return fig
    
    elif chart_type == "pie":
        group_col = [col for col in df.columns if col != cost_col][0]
        grouped = df.groupby(group_col)[cost_col].sum().sort_values(ascending=False).head(8)
        
        fig = px.pie(
            values=grouped.values,
            names=grouped.index,
            title=f'Cost Distribution by {group_col}'
        )
        return fig
    
    return None

# Main App
def main():
    st.set_page_config(
        page_title="FinOps GenAI Agent",
        page_icon="💰",
        layout="wide"
    )
    
    init_session_state()
    
    # Header with info
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="margin: 0; color: #1f77b4;">💰 FinOps GenAI Agent</h2>
        <p style="margin: 10px 0 0 0; color: #555;">
            <strong>Intelligent AWS Cost Analysis powered by AI</strong><br>
            Upload any AWS service SQL output and get instant insights, cost optimization recommendations, 
            and actionable analysis. The agent automatically detects your AWS service and generates 
            contextual questions tailored to your data.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload section (main page)
    st.subheader("📁 Upload Your Data")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Upload CSV file(s) - CUR, Trusted Advisor, Cost Optimization Hub, or any AWS data",
            type=['csv'],
            accept_multiple_files=True,
            help="Upload multiple files: CUR exports, Trusted Advisor reports, Cost Optimization Hub data, script outputs, etc. Agent will auto-detect and analyze."
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) loaded")
        else:
            st.info("👆 Upload to start")
    
    if uploaded_files:
        # Initialize multi-file storage
        if 'multi_file_data' not in st.session_state:
            st.session_state.multi_file_data = {}
        
        # Process multiple files
        import tempfile
        all_files_info = []
        
        for uploaded_file in uploaded_files:
            # Save uploaded file temporarily for DuckDB
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Read file for detection
            df = pd.read_csv(tmp_file_path)
            
            # Detect file type using intelligent detection
            file_type = detect_file_type(df, uploaded_file.name)
            
            # Store file info
            file_info = {
                'name': uploaded_file.name,
                'type': file_type,
                'path': tmp_file_path,
                'size': uploaded_file.size,
                'rows': len(df),
                'columns': len(df.columns),
                'df': df
            }
            all_files_info.append(file_info)
            st.session_state.multi_file_data[uploaded_file.name] = file_info
        
        # Display file detection results
        with st.expander("📁 Uploaded Files Detection", expanded=True):
            for file_info in all_files_info:
                col_a, col_b, col_c = st.columns([2, 2, 1])
                with col_a:
                    st.write(f"**{file_info['name']}**")
                with col_b:
                    st.write(f"🔍 Detected: **{file_info['type']}**")
                with col_c:
                    st.write(f"{file_info['rows']:,} rows")
        
        # Let user select which file to analyze (or merge)
        if len(uploaded_files) == 1:
            # Single file - use directly
            selected_file = all_files_info[0]
            df = selected_file['df']
            tmp_file_path = selected_file['path']
        else:
            # Multiple files - let user choose or merge
            st.markdown("### 📊 Analysis Options")
            
            file_options = [f"{f['name']} ({f['type']})" for f in all_files_info]
            file_options.insert(0, "🔗 Merge all files (if compatible)")
            
            selected_option = st.selectbox(
                "Choose analysis approach:",
                file_options,
                help="Select a single file to analyze, or merge compatible files"
            )
            
            if selected_option.startswith("🔗 Merge"):
                # Attempt to merge files
                merged_df, merge_success = merge_files(all_files_info)
                if merge_success:
                    df = merged_df
                    # Save merged file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                        df.to_csv(tmp_file.name, index=False)
                        tmp_file_path = tmp_file.name
                    st.success(f"✅ Merged {len(all_files_info)} files into {len(df):,} rows")
                else:
                    st.error("❌ Files are not compatible for merging. Please select a single file.")
                    return
            else:
                # Single file selected
                selected_idx = file_options.index(selected_option) - 1
                selected_file = all_files_info[selected_idx]
                df = selected_file['df']
                tmp_file_path = selected_file['path']
        
        # Use enhanced agent to load data (handles large files efficiently)
        agent = st.session_state.intelligent_agent
        if isinstance(agent, EnhancedAWSAgent):
            success = agent.load_data_from_file(tmp_file_path)
            if success:
                df = agent.data  # Get sample for display
            else:
                st.error("Failed to load data")
                return
        else:
            # Fallback to pandas for original agent
            agent.analyze_data(df)
        
        st.session_state.uploaded_data = df
        st.session_state.data_summary = analyze_uploaded_data(df)
        
        # Get analysis type from intelligent agent
        analysis_type = st.session_state.data_summary.get('aws_service', 'General Analysis')
        
        # Log file upload(s)
        for file_info in all_files_info:
            log_file_upload({
                'name': file_info['name'],
                'size': file_info['size'],
                'rows': file_info['rows'],
                'columns': file_info['columns'],
                'analysis_type': file_info['type']
            })
        
        # Data preview in expander
        with st.expander("👁️ Preview Data", expanded=False):
            st.dataframe(df.head(20), use_container_width=True)
    
    if st.session_state.uploaded_data is None:
        # Show helpful information when no data is uploaded
        st.markdown("---")
        
        st.markdown("""
        ### 🚀 How It Works
        
        1. **Upload** - Upload any CSV file from AWS Athena, Cost Explorer, or AWS service queries
        2. **Auto-Detect** - The intelligent agent automatically identifies your AWS service
        3. **Smart Questions** - Get contextual questions tailored to your specific data
        4. **AI Analysis** - Ask questions and receive detailed insights powered by AWS Bedrock
        5. **Visualizations** - Automatic charts and graphs for better understanding
        
        ### 📊 Supported AWS Services
        
        The agent works with **20+ AWS services** including:
        - **Compute**: EC2, Lambda, ECS, EKS
        - **Storage**: S3, EBS, EFS
        - **Database**: RDS, DynamoDB, Redshift
        - **Networking**: VPC, CloudFront, Route53, ELB
        - **Cost**: Cost & Usage Reports, Cost Explorer
        - **And many more...**
        
        ### 💡 What You Get
        
        - ✅ Automatic service detection
        - ✅ Smart, contextual questions
        - ✅ Cost optimization recommendations
        - ✅ Performance insights
        - ✅ Interactive visualizations
        - ✅ Actionable recommendations
        - ✅ AWS best practices
        """)
        
        st.markdown("---")
        
        # Show example queries
        st.subheader("📝 Example SQL Queries")
        
        tab1, tab2, tab3 = st.tabs(["Architecture Analysis", "Tagging Analysis", "Cost Analysis"])
        
        with tab1:
            with open('sql/athena_architecture_inference.sql', 'r') as f:
                st.code(f.read(), language='sql')
        
        with tab2:
            with open('sql/athena_tagging_correlation.sql', 'r') as f:
                st.code(f.read(), language='sql')
        
        with tab3:
            st.code("""
-- Simple Cost Analysis Query
SELECT 
    line_item_product_code as service,
    SUM(line_item_unblended_cost) as total_cost,
    COUNT(DISTINCT line_item_resource_id) as resource_count
FROM cost_and_usage_report
WHERE line_item_usage_start_date >= DATE_ADD('day', -30, CURRENT_DATE)
GROUP BY line_item_product_code
ORDER BY total_cost DESC
LIMIT 20;
            """, language='sql')
        
        return
    
    # Data summary
    summary = st.session_state.data_summary
    analysis_type = summary.get('aws_service', 'General Analysis')
    
    st.markdown("---")
    
    # Display AWS Service detected with prominent styling
    if 'aws_service' in summary:
        st.markdown(f"""
        <div style="background-color: #e8f4f8; padding: 15px; border-radius: 8px; border-left: 5px solid #1f77b4;">
            <h3 style="margin: 0; color: #1f77b4;">🔍 Detected: {summary['aws_service']}</h3>
            <p style="margin: 5px 0 0 0; color: #555;">
                The intelligent agent has analyzed your data and identified the AWS service.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Metrics in a clean layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Rows", f"{summary['total_rows']:,}")
    with col2:
        st.metric("💰 Total Cost", f"${summary['total_cost']:,.2f}" if summary['total_cost'] > 0 else "N/A")
    with col3:
        st.metric("📋 Columns", summary['total_columns'])
    with col4:
        st.metric("⏱️ Queries", st.session_state.query_count)
    
    # Show intelligent summary table
    agent = st.session_state.intelligent_agent
    if agent.data is not None:
        summary_table = agent.create_summary_table()
        if summary_table:
            with st.expander("📊 Detailed Summary Statistics", expanded=False):
                summary_df = pd.DataFrame(list(summary_table.items()), columns=['Metric', 'Value'])
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Suggested prompts in a better layout
    st.subheader("💡 Smart Questions for Your Data")
    st.caption("Click any question below or ask your own")
    
    suggested_prompts = generate_suggested_prompts(summary, analysis_type)
    
    # Display in 2 columns for better readability
    col1, col2 = st.columns(2)
    
    for idx, prompt in enumerate(suggested_prompts):
        with col1 if idx % 2 == 0 else col2:
            if st.button(prompt, key=f"prompt_{idx}", use_container_width=True):
                st.session_state.current_prompt = prompt
    
    st.markdown("---")
    
    # Chat interface with better styling
    st.subheader("💬 Interactive Analysis")
    
    # Add SQL query option for enhanced agent
    agent = st.session_state.intelligent_agent
    if isinstance(agent, EnhancedAWSAgent):
        with st.expander("🔧 Advanced: Execute SQL Query", expanded=False):
            st.caption("Write custom SQL queries for precise analysis")
            sql_query = st.text_area(
                "SQL Query",
                placeholder="SELECT service, SUM(cost) as total_cost FROM aws_data GROUP BY service ORDER BY total_cost DESC LIMIT 10",
                height=100
            )
            if st.button("Execute SQL"):
                if sql_query:
                    result, error = agent.execute_sql(sql_query)
                    if error:
                        st.error(f"SQL Error: {error}")
                    else:
                        st.success("Query executed successfully!")
                        st.dataframe(result, use_container_width=True)
                        
                        # Try to visualize if possible
                        if len(result.columns) >= 2:
                            fig = px.bar(result, x=result.columns[0], y=result.columns[1])
                            st.plotly_chart(fig, use_container_width=True)
    
    st.caption("Ask questions about your data or click a suggested question above")
    
    # Display chat history
    for idx, message in enumerate(st.session_state.chat_history):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "chart" in message:
                st.plotly_chart(message["chart"], use_container_width=True, key=f"chat_chart_{idx}")
    
    # Chat input
    user_input = st.chat_input("Ask me anything about your FinOps data...")
    
    # Handle suggested prompt click
    if 'current_prompt' in st.session_state:
        user_input = st.session_state.current_prompt
        del st.session_state.current_prompt
    
    if user_input:
        # Log user query
        is_suggested = 'current_prompt' in st.session_state
        log_user_query(user_input, {
            'is_suggested': is_suggested,
            'analysis_type': analysis_type,
            'has_data': st.session_state.uploaded_data is not None
        })
        
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing..."):
                start_time = datetime.now()
                
                # Prepare context
                context_data = {
                    "summary": summary,
                    "sample_data": st.session_state.uploaded_data.head(20).to_dict('records'),
                    "analysis_type": analysis_type
                }
                
                # Get LLM response
                response = call_bedrock_llm(user_input, context_data, st.session_state.chat_history)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                st.markdown(response)
                
                # Generate visualization if requested
                has_viz = any(word in user_input.lower() for word in ['chart', 'graph', 'visualize', 'show', 'plot'])
                if has_viz:
                    chart = create_cost_visualization(st.session_state.uploaded_data, "bar")
                    if chart:
                        st.plotly_chart(chart, use_container_width=True, key=f"response_chart_{len(st.session_state.chat_history)}")
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response,
                            "chart": chart
                        })
                    else:
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                else:
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                # Log agent response with metadata
                log_agent_response(user_input, response, {
                    'processing_time': processing_time,
                    'has_visualization': has_viz and chart is not None,
                    'analysis_type': analysis_type,
                    'data_summary': summary
                })
    
    # Actionable recommendations section (for enhanced agent)
    if isinstance(agent, EnhancedAWSAgent) and st.session_state.chat_history:
        st.markdown("---")
        st.subheader("🛠️ Actionable Recommendations")
        
        # Generate AWS CLI commands based on analysis
        last_response = st.session_state.chat_history[-1].get('content', '') if st.session_state.chat_history else ''
        commands = agent.generate_aws_cli_commands(last_response)
        
        if commands:
            st.caption("Ready-to-use AWS CLI commands based on your analysis")
            for cmd in commands:
                with st.expander(f"⚡ {cmd['action']}", expanded=False):
                    st.markdown(f"**Description:** {cmd['description']}")
                    st.markdown(f"**Risk Level:** `{cmd['risk']}`")
                    st.code(cmd['command'], language='bash')
                    st.warning("⚠️ Always review commands before executing in production!")
    
    # Visualization section
    st.markdown("---")
    st.subheader("📊 Data Visualizations")
    
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        chart1 = create_cost_visualization(st.session_state.uploaded_data, "bar")
        if chart1:
            st.plotly_chart(chart1, use_container_width=True, key="viz_bar_chart")
    
    with viz_col2:
        chart2 = create_cost_visualization(st.session_state.uploaded_data, "pie")
        if chart2:
            st.plotly_chart(chart2, use_container_width=True, key="viz_pie_chart")
    
    # Session info at bottom
    st.markdown("---")
    with st.expander("ℹ️ Session Information", expanded=False):
        session_duration = (datetime.now() - st.session_state.session_start).total_seconds()
        
        info_col1, info_col2, info_col3, info_col4 = st.columns(4)
        
        with info_col1:
            st.metric("Session Duration", f"{int(session_duration // 60)}m {int(session_duration % 60)}s")
        with info_col2:
            st.metric("Queries Made", st.session_state.query_count)
        with info_col3:
            st.metric("Files Uploaded", st.session_state.file_upload_count)
        with info_col4:
            st.metric("Messages", len(st.session_state.chat_history))
        
        st.caption(f"Session ID: `{st.session_state.session_id}`")
        
        if st.button("📝 End & Log Session"):
            log_session_end()
            st.success("✅ Session logged successfully!")

if __name__ == "__main__":
    main()
