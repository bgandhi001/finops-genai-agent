#!/usr/bin/env python3
"""
Analytics Dashboard for FinOps GenAI Agent
View usage statistics, user patterns, and system metrics
"""

import streamlit as st
import boto3
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import os
from pathlib import Path

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

load_env_file()

@st.cache_resource
def get_dynamodb_client():
    return boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))

def fetch_analytics_data(days=7):
    """Fetch analytics data from DynamoDB"""
    try:
        dynamodb = get_dynamodb_client()
        table_name = os.getenv('DYNAMODB_TABLE', 'finops-agent-interactions')
        table = dynamodb.Table(table_name)
        
        # Scan table (in production, use better query patterns)
        response = table.scan()
        items = response['Items']
        
        # Continue scanning if there are more items
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        
        # Filter by date range
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_items = [
            item for item in items
            if datetime.fromisoformat(item.get('timestamp', '2000-01-01')) >= cutoff_date
        ]
        
        return filtered_items
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return []

def calculate_metrics(data):
    """Calculate key metrics from analytics data"""
    metrics = {
        'total_sessions': len([d for d in data if d.get('event_type') == 'session_start']),
        'total_queries': len([d for d in data if d.get('event_type') == 'user_query']),
        'total_uploads': len([d for d in data if d.get('event_type') == 'file_upload']),
        'total_responses': len([d for d in data if d.get('event_type') == 'agent_response']),
        'avg_session_duration': 0,
        'avg_queries_per_session': 0,
        'avg_response_time': 0
    }
    
    # Calculate averages
    session_ends = [d for d in data if d.get('event_type') == 'session_end']
    if session_ends:
        metrics['avg_session_duration'] = sum(float(s.get('session_duration', 0)) for s in session_ends) / len(session_ends)
        metrics['avg_queries_per_session'] = sum(int(s.get('total_queries', 0)) for s in session_ends) / len(session_ends)
    
    responses = [d for d in data if d.get('event_type') == 'agent_response']
    if responses:
        metrics['avg_response_time'] = sum(float(r.get('processing_time', 0)) for r in responses) / len(responses)
    
    return metrics

def main():
    st.set_page_config(
        page_title="FinOps Agent Analytics",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 FinOps GenAI Agent - Analytics Dashboard")
    st.markdown("---")
    
    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        days = st.slider("Days to analyze", 1, 90, 7)
        
        if st.button("🔄 Refresh Data"):
            st.cache_resource.clear()
            st.rerun()
    
    # Fetch data
    with st.spinner("Loading analytics data..."):
        data = fetch_analytics_data(days)
    
    if not data:
        st.warning("No analytics data available. Start using the app to generate data!")
        return
    
    # Calculate metrics
    metrics = calculate_metrics(data)
    
    # Display key metrics
    st.subheader("📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sessions", metrics['total_sessions'])
    with col2:
        st.metric("Total Queries", metrics['total_queries'])
    with col3:
        st.metric("Files Uploaded", metrics['total_uploads'])
    with col4:
        st.metric("Avg Response Time", f"{metrics['avg_response_time']:.2f}s")
    
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric("Avg Session Duration", f"{int(metrics['avg_session_duration'] // 60)}m {int(metrics['avg_session_duration'] % 60)}s")
    with col6:
        st.metric("Queries/Session", f"{metrics['avg_queries_per_session']:.1f}")
    with col7:
        st.metric("Total Responses", metrics['total_responses'])
    with col8:
        completion_rate = (metrics['total_responses'] / metrics['total_queries'] * 100) if metrics['total_queries'] > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    st.markdown("---")
    
    # Activity over time
    st.subheader("📅 Activity Over Time")
    
    df = pd.DataFrame(data)
    if not df.empty and 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        daily_activity = df.groupby(['date', 'event_type']).size().reset_index(name='count')
        
        fig = px.line(
            daily_activity,
            x='date',
            y='count',
            color='event_type',
            title='Daily Activity by Event Type',
            labels={'count': 'Number of Events', 'date': 'Date'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Analysis type distribution
    st.markdown("---")
    st.subheader("🎯 Analysis Type Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        queries = [d for d in data if d.get('event_type') == 'user_query']
        if queries:
            analysis_types = [q.get('analysis_type', 'unknown') for q in queries]
            type_counts = Counter(analysis_types)
            
            fig = px.pie(
                values=list(type_counts.values()),
                names=list(type_counts.keys()),
                title='Queries by Analysis Type'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        uploads = [d for d in data if d.get('event_type') == 'file_upload']
        if uploads:
            upload_types = [u.get('analysis_type', 'unknown') for u in uploads]
            upload_counts = Counter(upload_types)
            
            fig = px.pie(
                values=list(upload_counts.values()),
                names=list(upload_counts.keys()),
                title='Uploads by Analysis Type'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Query patterns
    st.markdown("---")
    st.subheader("💬 Query Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if queries:
            suggested_count = sum(1 for q in queries if q.get('is_suggested_prompt', False))
            custom_count = len(queries) - suggested_count
            
            fig = go.Figure(data=[
                go.Bar(name='Suggested Prompts', x=['Queries'], y=[suggested_count]),
                go.Bar(name='Custom Queries', x=['Queries'], y=[custom_count])
            ])
            fig.update_layout(title='Suggested vs Custom Queries', barmode='stack')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        responses = [d for d in data if d.get('event_type') == 'agent_response']
        if responses:
            viz_count = sum(1 for r in responses if r.get('has_visualization', False))
            no_viz_count = len(responses) - viz_count
            
            fig = go.Figure(data=[
                go.Bar(name='With Visualization', x=['Responses'], y=[viz_count]),
                go.Bar(name='Text Only', x=['Responses'], y=[no_viz_count])
            ])
            fig.update_layout(title='Responses with Visualizations', barmode='stack')
            st.plotly_chart(fig, use_container_width=True)
    
    # File upload statistics
    st.markdown("---")
    st.subheader("📁 File Upload Statistics")
    
    if uploads:
        upload_df = pd.DataFrame(uploads)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'row_count' in upload_df.columns:
                fig = px.histogram(
                    upload_df,
                    x='row_count',
                    title='Distribution of File Sizes (Rows)',
                    labels={'row_count': 'Number of Rows'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'file_size' in upload_df.columns:
                upload_df['file_size_mb'] = upload_df['file_size'] / (1024 * 1024)
                fig = px.histogram(
                    upload_df,
                    x='file_size_mb',
                    title='Distribution of File Sizes (MB)',
                    labels={'file_size_mb': 'File Size (MB)'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.markdown("---")
    st.subheader("🕐 Recent Activity")
    
    recent_data = sorted(data, key=lambda x: x.get('timestamp', ''), reverse=True)[:20]
    
    if recent_data:
        activity_df = pd.DataFrame([
            {
                'Timestamp': d.get('timestamp', ''),
                'Event Type': d.get('event_type', ''),
                'Session ID': d.get('session_id', '')[:8] + '...',
                'Details': get_event_details(d)
            }
            for d in recent_data
        ])
        
        st.dataframe(activity_df, use_container_width=True)
    
    # Export data
    st.markdown("---")
    st.subheader("📥 Export Data")
    
    if st.button("Export Analytics to CSV"):
        export_df = pd.DataFrame(data)
        csv = export_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"finops_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def get_event_details(event):
    """Get human-readable event details"""
    event_type = event.get('event_type', '')
    
    if event_type == 'user_query':
        query = event.get('user_query', '')
        return f"Query: {query[:50]}..." if len(query) > 50 else f"Query: {query}"
    elif event_type == 'file_upload':
        return f"File: {event.get('file_name', 'unknown')} ({event.get('row_count', 0)} rows)"
    elif event_type == 'session_start':
        return "Session started"
    elif event_type == 'session_end':
        return f"Session ended ({event.get('total_queries', 0)} queries)"
    elif event_type == 'agent_response':
        return f"Response ({event.get('processing_time', 0):.2f}s)"
    else:
        return event_type

if __name__ == "__main__":
    main()
