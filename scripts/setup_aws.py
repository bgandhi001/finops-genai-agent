#!/usr/bin/env python3
"""
AWS Infrastructure Setup Script for FinOps GenAI Agent
Creates necessary AWS resources: DynamoDB table for learning storage
"""

import boto3
import sys
import os
from pathlib import Path

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path('.env')
    if env_file.exists():
        print("📄 Loading credentials from .env file...")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        return True
    return False

def create_dynamodb_table(table_name='finops-agent-interactions', region='us-east-1'):
    """Create DynamoDB table for storing user interactions"""
    try:
        dynamodb = boto3.client('dynamodb', region_name=region)
        
        print(f"Creating DynamoDB table: {table_name}...")
        
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'interaction_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'interaction_id',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {
                    'Key': 'Application',
                    'Value': 'FinOps-GenAI-Agent'
                },
                {
                    'Key': 'Purpose',
                    'Value': 'Learning-Storage'
                }
            ]
        )
        
        print(f"✅ Table {table_name} created successfully!")
        print(f"   ARN: {response['TableDescription']['TableArn']}")
        return True
        
    except dynamodb.exceptions.ResourceInUseException:
        print(f"ℹ️  Table {table_name} already exists")
        return True
    except Exception as e:
        print(f"❌ Error creating table: {str(e)}")
        return False

def check_bedrock_access(region='us-east-1'):
    """Verify Bedrock access"""
    try:
        bedrock = boto3.client('bedrock-runtime', region_name=region)
        print("✅ AWS Bedrock access verified")
        return True
    except Exception as e:
        print(f"⚠️  Bedrock access check failed: {str(e)}")
        print("   Please ensure Bedrock is enabled in your AWS account")
        return False

def setup_iam_policy():
    """Print IAM policy needed for the application"""
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                "Resource": "arn:aws:dynamodb:*:*:table/finops-agent-interactions"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "athena:StartQueryExecution",
                    "athena:GetQueryExecution",
                    "athena:GetQueryResults"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::your-athena-results-bucket/*",
                    "arn:aws:s3:::your-cur-bucket/*"
                ]
            }
        ]
    }
    
    print("\n📋 Required IAM Policy:")
    print("=" * 60)
    import json
    print(json.dumps(policy, indent=2))
    print("=" * 60)

def main():
    print("🚀 FinOps GenAI Agent - AWS Setup")
    print("=" * 60)
    print()
    
    # Load .env file
    env_loaded = load_env_file()
    
    # Get configuration
    region = os.getenv('AWS_REGION', 'us-east-1')
    table_name = os.getenv('DYNAMODB_TABLE', 'finops-agent-interactions')
    
    print(f"Region: {region}")
    print(f"DynamoDB Table: {table_name}")
    print()
    
    # Check AWS credentials
    try:
        sts = boto3.client('sts', region_name=region)
        identity = sts.get_caller_identity()
        print(f"✅ AWS Credentials configured")
        print(f"   Account: {identity['Account']}")
        print(f"   User/Role: {identity['Arn']}")
        print()
    except Exception as e:
        print(f"❌ AWS credentials not configured: {str(e)}")
        print()
        print("📝 To fix this, you have 3 options:")
        print()
        print("Option 1: Edit .env file (Recommended)")
        print("   1. Open .env file in a text editor")
        print("   2. Replace 'your_access_key_here' with your actual AWS Access Key")
        print("   3. Replace 'your_secret_key_here' with your actual AWS Secret Key")
        print("   4. Run this script again")
        print()
        print("Option 2: Set environment variables")
        print("   export AWS_ACCESS_KEY_ID=your_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret")
        print()
        print("Option 3: Install and configure AWS CLI")
        print("   brew install awscli  # macOS")
        print("   aws configure")
        print()
        print("📚 See AWS_CLI_SETUP.md for detailed instructions")
        print()
        sys.exit(1)
    
    # Create DynamoDB table
    if not create_dynamodb_table(table_name, region):
        sys.exit(1)
    
    print()
    
    # Check Bedrock access
    check_bedrock_access(region)
    
    print()
    
    # Print IAM policy
    setup_iam_policy()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Ensure the IAM policy above is attached to your user/role")
    print("2. Enable Bedrock model access in AWS Console (Claude 3 Sonnet)")
    print("3. Run: streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()
