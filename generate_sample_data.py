#!/usr/bin/env python3
"""
Generate sample CSV data for testing the FinOps GenAI Agent
without needing actual AWS CUR data
"""

import pandas as pd
import random
from datetime import datetime, timedelta

def generate_architecture_sample():
    """Generate sample data for architecture inference"""
    data = []
    
    products = ['AmazonEC2', 'AmazonRDS', 'AmazonS3', 'AmazonDynamoDB']
    usage_types = [
        'USE2-DataTransfer-Regional-Bytes',
        'USE1-DataTransfer-Regional-Bytes',
        'NatGateway-Bytes',
        'EBS:VolumeUsage.gp2',
        'EBS:VolumeUsage.gp3'
    ]
    azs = ['us-east-1a', 'us-east-1b', 'us-east-1c', 'us-east-2a', 'us-east-2b']
    
    for _ in range(50):
        data.append({
            'line_item_product_code': random.choice(products),
            'line_item_usage_type': random.choice(usage_types),
            'resource_tags_user_name': f'resource-{random.randint(1, 20)}',
            'line_item_availability_zone': random.choice(azs),
            'total_gb': round(random.uniform(100, 50000), 2),
            'total_cost': round(random.uniform(10, 5000), 2)
        })
    
    df = pd.DataFrame(data)
    df.to_csv('sample_architecture_data.csv', index=False)
    print("✅ Generated: sample_architecture_data.csv")
    return df

def generate_tagging_sample():
    """Generate sample data for tagging analysis"""
    data = []
    
    projects = ['PaymentsAPI', 'DataPipeline', 'WebApp', 'Analytics', None, None]
    cost_centers = ['CC-998', 'CC-765', 'CC-432', None]
    
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(40):
        # Create clusters of resources at same time
        cluster_time = base_time + timedelta(hours=random.randint(0, 720))
        
        for j in range(random.randint(1, 4)):
            project = random.choice(projects)
            data.append({
                'untagged_resource': f'vol-{random.randint(100000, 999999)}' if project is None else None,
                'first_seen_time': cluster_time.isoformat(),
                'untagged_spend': round(random.uniform(5, 500), 2) if project is None else 0,
                'tagged_neighbor': f'i-{random.randint(100000, 999999)}',
                'neighbor_project': project,
                'neighbor_cost_center': random.choice(cost_centers) if project else None
            })
    
    # Filter to only untagged resources
    df = pd.DataFrame(data)
    df = df[df['untagged_resource'].notna()]
    df.to_csv('sample_tagging_data.csv', index=False)
    print("✅ Generated: sample_tagging_data.csv")
    return df

def generate_cost_analysis_sample():
    """Generate sample data for general cost analysis"""
    data = []
    
    services = [
        'Amazon Elastic Compute Cloud',
        'Amazon Relational Database Service',
        'Amazon Simple Storage Service',
        'Amazon DynamoDB',
        'AWS Lambda',
        'Amazon CloudFront',
        'Amazon ElastiCache',
        'Amazon Elastic Load Balancing'
    ]
    
    regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
    
    start_date = datetime.now() - timedelta(days=30)
    
    for day in range(30):
        current_date = start_date + timedelta(days=day)
        
        for service in services:
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'service': service,
                'region': random.choice(regions),
                'usage_amount': round(random.uniform(100, 10000), 2),
                'total_cost': round(random.uniform(50, 2000), 2),
                'resource_count': random.randint(5, 100)
            })
    
    df = pd.DataFrame(data)
    df.to_csv('sample_cost_analysis.csv', index=False)
    print("✅ Generated: sample_cost_analysis.csv")
    return df

def main():
    print("🎲 Generating Sample Data for FinOps GenAI Agent")
    print("=" * 60)
    
    print("\n1. Architecture Inference Data...")
    arch_df = generate_architecture_sample()
    print(f"   Rows: {len(arch_df)}")
    
    print("\n2. Tagging Analysis Data...")
    tag_df = generate_tagging_sample()
    print(f"   Rows: {len(tag_df)}")
    
    print("\n3. General Cost Analysis Data...")
    cost_df = generate_cost_analysis_sample()
    print(f"   Rows: {len(cost_df)}")
    
    print("\n" + "=" * 60)
    print("✅ All sample files generated!")
    print("\nYou can now upload these CSV files to the Streamlit app:")
    print("  - sample_architecture_data.csv")
    print("  - sample_tagging_data.csv")
    print("  - sample_cost_analysis.csv")

if __name__ == "__main__":
    main()
