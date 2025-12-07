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
    df.to_csv('sample_data/sample_architecture_data.csv', index=False)
    print("✅ Generated: sample_data/sample_architecture_data.csv")
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
    df.to_csv('sample_data/sample_tagging_data.csv', index=False)
    print("✅ Generated: sample_data/sample_tagging_data.csv")
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
    df.to_csv('sample_data/sample_cost_analysis.csv', index=False)
    print("✅ Generated: sample_data/sample_cost_analysis.csv")
    return df

def generate_ebs_unattached_sample():
    """Generate sample data for unattached EBS volumes"""
    data = []
    
    volume_types = ['gp2', 'gp3', 'io1', 'io2', 'st1', 'sc1']
    regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1', 'us-east-2']
    states = ['available', 'in-use']
    
    # Generate volumes with some unattached
    for i in range(150):
        state = random.choices(states, weights=[30, 70])[0]  # 30% unattached
        volume_type = random.choice(volume_types)
        size_gb = random.choice([8, 16, 32, 50, 100, 200, 500, 1000])
        
        # Calculate cost based on volume type and size
        cost_per_gb = {
            'gp2': 0.10,
            'gp3': 0.08,
            'io1': 0.125,
            'io2': 0.125,
            'st1': 0.045,
            'sc1': 0.025
        }
        
        monthly_cost = size_gb * cost_per_gb[volume_type]
        days_unattached = random.randint(1, 180) if state == 'available' else 0
        
        data.append({
            'volume_id': f'vol-{random.randint(100000000, 999999999):09x}',
            'volume_type': volume_type,
            'size_gb': size_gb,
            'state': state,
            'region': random.choice(regions),
            'availability_zone': f"{random.choice(regions)}{random.choice(['a', 'b', 'c'])}",
            'create_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
            'days_unattached': days_unattached,
            'monthly_cost': round(monthly_cost, 2),
            'wasted_cost': round(monthly_cost * (days_unattached / 30), 2) if state == 'available' else 0,
            'iops': random.randint(3000, 16000) if volume_type in ['io1', 'io2'] else 3000,
            'throughput_mbps': random.choice([125, 250, 500, 1000]) if volume_type == 'gp3' else None,
            'last_attached_instance': f'i-{random.randint(100000000, 999999999):09x}' if state == 'available' else None,
            'snapshot_id': f'snap-{random.randint(100000000, 999999999):09x}' if random.random() > 0.5 else None,
            'encrypted': random.choice([True, False]),
            'tags_project': random.choice(['WebApp', 'DataPipeline', 'Analytics', 'Testing', None]),
            'tags_environment': random.choice(['production', 'staging', 'development', 'test', None])
        })
    
    df = pd.DataFrame(data)
    df.to_csv('sample_data/sample_ebs_volumes.csv', index=False)
    print("✅ Generated: sample_data/sample_ebs_volumes.csv")
    print(f"   Total volumes: {len(df)}")
    print(f"   Unattached: {len(df[df['state'] == 'available'])}")
    print(f"   Potential savings: ${df['wasted_cost'].sum():.2f}/month")
    return df

def generate_s3_unused_buckets_sample():
    """Generate sample data for S3 buckets with no GET/PUT operations"""
    data = []
    
    regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1', 'us-east-2']
    storage_classes = ['STANDARD', 'STANDARD_IA', 'INTELLIGENT_TIERING', 'GLACIER', 'DEEP_ARCHIVE']
    
    # Generate buckets with varying activity levels
    for i in range(80):
        bucket_name = f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=15))}-bucket"
        storage_class = random.choice(storage_classes)
        size_gb = round(random.uniform(0.1, 5000), 2)
        
        # Some buckets have no activity
        has_activity = random.random() > 0.35  # 35% have no activity
        
        get_requests = random.randint(100, 100000) if has_activity else 0
        put_requests = random.randint(10, 10000) if has_activity else 0
        
        # Calculate costs
        storage_cost_per_gb = {
            'STANDARD': 0.023,
            'STANDARD_IA': 0.0125,
            'INTELLIGENT_TIERING': 0.023,
            'GLACIER': 0.004,
            'DEEP_ARCHIVE': 0.00099
        }
        
        monthly_storage_cost = size_gb * storage_cost_per_gb[storage_class]
        request_cost = (get_requests * 0.0004 / 1000) + (put_requests * 0.005 / 1000)
        
        days_inactive = random.randint(30, 730) if not has_activity else 0
        
        data.append({
            'bucket_name': bucket_name,
            'region': random.choice(regions),
            'storage_class': storage_class,
            'size_gb': size_gb,
            'object_count': random.randint(1, 1000000),
            'create_date': (datetime.now() - timedelta(days=random.randint(30, 1095))).strftime('%Y-%m-%d'),
            'last_modified_date': (datetime.now() - timedelta(days=days_inactive)).strftime('%Y-%m-%d'),
            'days_inactive': days_inactive,
            'get_requests_30d': get_requests,
            'put_requests_30d': put_requests,
            'monthly_storage_cost': round(monthly_storage_cost, 2),
            'monthly_request_cost': round(request_cost, 2),
            'total_monthly_cost': round(monthly_storage_cost + request_cost, 2),
            'wasted_cost': round(monthly_storage_cost, 2) if not has_activity else 0,
            'versioning_enabled': random.choice([True, False]),
            'lifecycle_policy': random.choice([True, False]),
            'public_access': random.choice([True, False]),
            'encryption': random.choice(['AES256', 'aws:kms', None]),
            'tags_project': random.choice(['WebApp', 'DataPipeline', 'Analytics', 'Backup', 'Archive', None]),
            'tags_owner': random.choice(['team-a', 'team-b', 'team-c', 'team-d', None])
        })
    
    df = pd.DataFrame(data)
    df.to_csv('sample_data/sample_s3_buckets.csv', index=False)
    print("✅ Generated: sample_data/sample_s3_buckets.csv")
    print(f"   Total buckets: {len(df)}")
    print(f"   Inactive buckets: {len(df[df['days_inactive'] > 0])}")
    print(f"   Potential savings: ${df['wasted_cost'].sum():.2f}/month")
    return df

def generate_monthly_trend_sample():
    """Generate 12 months of trend data for multiple services"""
    data = []
    
    services = {
        'Amazon EC2': {'base': 5000, 'trend': 'increasing', 'volatility': 500},
        'Amazon RDS': {'base': 2000, 'trend': 'stable', 'volatility': 200},
        'Amazon S3': {'base': 1500, 'trend': 'increasing', 'volatility': 300},
        'Amazon DynamoDB': {'base': 800, 'trend': 'increasing', 'volatility': 150},
        'AWS Lambda': {'base': 400, 'trend': 'increasing', 'volatility': 100},
        'Amazon CloudFront': {'base': 600, 'trend': 'stable', 'volatility': 80},
        'Amazon EBS': {'base': 1200, 'trend': 'increasing', 'volatility': 150},
        'Amazon ElastiCache': {'base': 500, 'trend': 'stable', 'volatility': 50},
        'NAT Gateway': {'base': 300, 'trend': 'stable', 'volatility': 40},
        'Elastic Load Balancing': {'base': 250, 'trend': 'stable', 'volatility': 30}
    }
    
    regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
    
    # Generate 12 months of data
    start_date = datetime.now() - timedelta(days=365)
    
    for month in range(12):
        current_date = start_date + timedelta(days=30 * month)
        month_str = current_date.strftime('%Y-%m')
        
        for service, config in services.items():
            for region in regions:
                # Calculate cost with trend
                base_cost = config['base']
                
                if config['trend'] == 'increasing':
                    trend_factor = 1 + (month * 0.05)  # 5% growth per month
                elif config['trend'] == 'decreasing':
                    trend_factor = 1 - (month * 0.03)  # 3% decrease per month
                else:
                    trend_factor = 1
                
                # Add some randomness
                volatility = random.uniform(-config['volatility'], config['volatility'])
                monthly_cost = (base_cost * trend_factor + volatility) / len(regions)
                
                # Calculate usage metrics
                usage_hours = random.randint(500, 730)
                resource_count = random.randint(5, 50)
                
                data.append({
                    'month': month_str,
                    'service': service,
                    'region': region,
                    'monthly_cost': round(monthly_cost, 2),
                    'usage_hours': usage_hours,
                    'resource_count': resource_count,
                    'avg_cost_per_resource': round(monthly_cost / resource_count, 2),
                    'cost_change_pct': round((trend_factor - 1) * 100, 1) if month > 0 else 0,
                    'forecast_next_month': round(monthly_cost * 1.05, 2) if config['trend'] == 'increasing' else round(monthly_cost, 2)
                })
    
    df = pd.DataFrame(data)
    df.to_csv('sample_data/sample_monthly_trends.csv', index=False)
    print("✅ Generated: sample_data/sample_monthly_trends.csv")
    print(f"   Months: 12")
    print(f"   Services: {len(services)}")
    print(f"   Total records: {len(df)}")
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
    
    print("\n4. EBS Volumes (Unattached) Data...")
    ebs_df = generate_ebs_unattached_sample()
    
    print("\n5. S3 Buckets (Unused) Data...")
    s3_df = generate_s3_unused_buckets_sample()
    
    print("\n6. Monthly Trend Analysis Data...")
    trend_df = generate_monthly_trend_sample()
    
    print("\n" + "=" * 60)
    print("✅ All sample files generated in sample_data/ folder!")
    print("\nYou can now upload these CSV files to the Streamlit app:")
    print("  - sample_data/sample_architecture_data.csv")
    print("  - sample_data/sample_tagging_data.csv")
    print("  - sample_data/sample_cost_analysis.csv")
    print("  - sample_data/sample_ebs_volumes.csv (NEW)")
    print("  - sample_data/sample_s3_buckets.csv (NEW)")
    print("  - sample_data/sample_monthly_trends.csv (NEW)")
    print("\n💡 Use these datasets to train and test the agent's capabilities!")

if __name__ == "__main__":
    main()
