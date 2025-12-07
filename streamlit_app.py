import streamlit as st
import pandas as pd
import json
import boto3
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import os

# AWS Bedrock client initialization
@st.cache_resource
def get_bedrock_client():
    return boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))

@st.cache_resource
def get_dynamodb_client():
    return boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))

# Initialize session state
def init_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None
    if 'data_summary' not in st.session_state:
        st.session_state.data_summary = None
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {}

def analyze_uploaded_data(df):
    """Analyze uploaded data and generate summary"""
    summary = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': df.columns.tolist(),
        'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
        'total_cost': df['total_cost'].sum() if 'total_cost' in df.columns else 0,
        'date_range': None
    }
    
    # Detect cost columns
    cost_cols = [col for col in df.columns if 'cost' in col.lower() or 'spend' in col.lower()]
    if cost_cols:
        summary['total_cost'] = df[cost_cols[0]].sum()
    
    return summary

def generate_suggested_prompts(data_summary, analysis_type):
    """Generate contextual prompts based on uploaded data"""
    prompts = []
    
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

def call_bedrock_llm(prompt, context_data, chat_history):
    """Call AWS Bedrock with Claude for analysis"""
    try:
        bedrock = get_bedrock_client()
        
        # Build conversation context
        conversation_context = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in chat_history[-5:]  # Last 5 messages for context
        ])
        
        full_prompt = f"""You are an expert FinOps Architect Assistant with deep knowledge of AWS cost optimization.

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
                    "content": full_prompt
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

def save_interaction_to_dynamodb(user_query, agent_response, data_context):
    """Save user interactions for learning"""
    try:
        dynamodb = get_dynamodb_client()
        table_name = os.getenv('DYNAMODB_TABLE', 'finops-agent-interactions')
        table = dynamodb.Table(table_name)
        
        item = {
            'interaction_id': f"{datetime.now().timestamp()}",
            'timestamp': datetime.now().isoformat(),
            'user_query': user_query,
            'agent_response': agent_response,
            'data_context': json.dumps(data_context),
            'session_id': st.session_state.get('session_id', 'unknown')
        }
        
        table.put_item(Item=item)
    except Exception as e:
        st.warning(f"Could not save interaction: {str(e)}")

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
    
    # Sidebar
    with st.sidebar:
        st.title("💰 FinOps GenAI Agent")
        st.markdown("---")
        
        # Analysis type selection
        analysis_type = st.selectbox(
            "Analysis Type",
            ["Architecture Inference", "Tagging Analysis", "General Cost Analysis"]
        )
        
        st.markdown("---")
        
        # File upload
        st.subheader("📁 Upload SQL Output")
        uploaded_file = st.file_uploader(
            "Upload CSV file from Athena query",
            type=['csv'],
            help="Upload the output from your Athena SQL queries"
        )
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.session_state.uploaded_data = df
            st.session_state.data_summary = analyze_uploaded_data(df)
            st.success(f"✅ Loaded {len(df)} rows")
            
            with st.expander("📊 Data Preview"):
                st.dataframe(df.head(10), use_container_width=True)
        
        st.markdown("---")
        
        # AWS Configuration
        with st.expander("⚙️ AWS Configuration"):
            aws_region = st.text_input("AWS Region", value="us-east-1")
            dynamodb_table = st.text_input("DynamoDB Table", value="finops-agent-interactions")
            
            if st.button("Save Config"):
                os.environ['AWS_REGION'] = aws_region
                os.environ['DYNAMODB_TABLE'] = dynamodb_table
                st.success("Configuration saved!")
    
    # Main content
    st.title("🤖 FinOps GenAI Agent - Interactive Analysis")
    
    if st.session_state.uploaded_data is None:
        st.info("👈 Please upload a CSV file from your Athena query to begin analysis")
        
        # Show example queries
        st.subheader("📝 Example SQL Queries")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Architecture Inference Query**")
            with open('athena_architecture_inference.sql', 'r') as f:
                st.code(f.read(), language='sql')
        
        with col2:
            st.markdown("**Tagging Correlation Query**")
            with open('athena_tagging_correlation.sql', 'r') as f:
                st.code(f.read(), language='sql')
        
        return
    
    # Data summary
    summary = st.session_state.data_summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Rows", f"{summary['total_rows']:,}")
    with col2:
        st.metric("Total Cost", f"${summary['total_cost']:,.2f}")
    with col3:
        st.metric("Columns", summary['total_columns'])
    with col4:
        st.metric("Analysis Type", analysis_type)
    
    st.markdown("---")
    
    # Suggested prompts
    st.subheader("💡 Suggested Questions")
    suggested_prompts = generate_suggested_prompts(summary, analysis_type)
    
    cols = st.columns(len(suggested_prompts))
    for idx, (col, prompt) in enumerate(zip(cols, suggested_prompts)):
        with col:
            if st.button(prompt, key=f"prompt_{idx}", use_container_width=True):
                st.session_state.current_prompt = prompt
    
    st.markdown("---")
    
    # Chat interface
    st.subheader("💬 Chat with Agent")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "chart" in message:
                st.plotly_chart(message["chart"], use_container_width=True)
    
    # Chat input
    user_input = st.chat_input("Ask me anything about your FinOps data...")
    
    # Handle suggested prompt click
    if 'current_prompt' in st.session_state:
        user_input = st.session_state.current_prompt
        del st.session_state.current_prompt
    
    if user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing..."):
                # Prepare context
                context_data = {
                    "summary": summary,
                    "sample_data": st.session_state.uploaded_data.head(20).to_dict('records'),
                    "analysis_type": analysis_type
                }
                
                # Get LLM response
                response = call_bedrock_llm(user_input, context_data, st.session_state.chat_history)
                
                st.markdown(response)
                
                # Generate visualization if requested
                if any(word in user_input.lower() for word in ['chart', 'graph', 'visualize', 'show', 'plot']):
                    chart = create_cost_visualization(st.session_state.uploaded_data, "bar")
                    if chart:
                        st.plotly_chart(chart, use_container_width=True)
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response,
                            "chart": chart
                        })
                    else:
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
                else:
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                # Save interaction for learning
                save_interaction_to_dynamodb(user_input, response, context_data)
    
    # Visualization section
    st.markdown("---")
    st.subheader("📊 Data Visualizations")
    
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        chart1 = create_cost_visualization(st.session_state.uploaded_data, "bar")
        if chart1:
            st.plotly_chart(chart1, use_container_width=True)
    
    with viz_col2:
        chart2 = create_cost_visualization(st.session_state.uploaded_data, "pie")
        if chart2:
            st.plotly_chart(chart2, use_container_width=True)

if __name__ == "__main__":
    main()
