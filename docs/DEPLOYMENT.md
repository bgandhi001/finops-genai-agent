# Deployment Guide - FinOps GenAI Agent

## 🚀 Deployment Options

### Option 1: Local Development (Fastest)

#### Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup AWS resources
python setup_aws.py

# Run the app
streamlit run streamlit_app.py

# When done, deactivate
deactivate
```

#### Using System Python (Not Recommended)

```bash
# Install dependencies globally
pip install -r requirements.txt

# Setup AWS resources
python setup_aws.py

# Run the app
streamlit run streamlit_app.py
```

Access at: `http://localhost:8501`

---

### Option 2: Docker (Recommended for Production)

#### Build and Run

```bash
# Build image
docker build -t finops-agent .

# Run container
docker run -p 8501:8501 \
  -e AWS_REGION=us-east-1 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e DYNAMODB_TABLE=finops-agent-interactions \
  finops-agent
```

#### Using Docker Compose

```bash
# Create .env file with credentials
cp .env.example .env
# Edit .env with your AWS credentials

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

### Option 3: AWS ECS/Fargate (Scalable)

#### Prerequisites
- AWS CLI configured
- ECS cluster created
- ECR repository created

#### Steps

1. **Build and push to ECR**

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t finops-agent .

# Tag image
docker tag finops-agent:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/finops-agent:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/finops-agent:latest
```

2. **Create ECS Task Definition**

```json
{
  "family": "finops-agent",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "taskRoleArn": "arn:aws:iam::<account-id>:role/FinOpsAgentTaskRole",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "finops-agent",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/finops-agent:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "AWS_REGION",
          "value": "us-east-1"
        },
        {
          "name": "DYNAMODB_TABLE",
          "value": "finops-agent-interactions"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/finops-agent",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

3. **Create ECS Service**

```bash
aws ecs create-service \
  --cluster finops-cluster \
  --service-name finops-agent-service \
  --task-definition finops-agent \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

4. **Setup Application Load Balancer (Optional)**

```bash
# Create target group
aws elbv2 create-target-group \
  --name finops-agent-tg \
  --protocol HTTP \
  --port 8501 \
  --vpc-id vpc-xxx \
  --target-type ip

# Create ALB and listener
# Configure health check to /_stcore/health
```

---

### Option 4: AWS EC2 (Simple)

#### Launch EC2 Instance

```bash
# Launch Amazon Linux 2 instance
# Attach IAM role with required permissions
# SSH into instance

# Install dependencies
sudo yum update -y
sudo yum install python3 python3-pip git -y

# Clone repository
git clone https://github.com/bgandhi001/finops-genai-agent.git
cd finops-genai-agent

# Install Python packages
pip3 install -r requirements.txt

# Setup AWS resources
python3 setup_aws.py

# Run with systemd (persistent)
sudo tee /etc/systemd/system/finops-agent.service > /dev/null <<EOF
[Unit]
Description=FinOps GenAI Agent
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/finops-genai-agent
ExecStart=/usr/bin/python3 -m streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable finops-agent
sudo systemctl start finops-agent

# Check status
sudo systemctl status finops-agent
```

#### Configure Security Group
- Allow inbound TCP 8501 from your IP
- Allow outbound HTTPS (443) for AWS API calls

---

### Option 5: Streamlit Cloud (Easiest)

1. **Push to GitHub**
```bash
git add .
git commit -m "Add Streamlit app"
git push origin main
```

2. **Deploy on Streamlit Cloud**
- Go to https://share.streamlit.io/
- Connect your GitHub repository
- Select `streamlit_app.py` as main file
- Add secrets in dashboard:
  ```toml
  AWS_REGION = "us-east-1"
  AWS_ACCESS_KEY_ID = "your_key"
  AWS_SECRET_ACCESS_KEY = "your_secret"
  DYNAMODB_TABLE = "finops-agent-interactions"
  ```
- Click Deploy

---

## 🔒 IAM Role Configuration

### For ECS Task Role

```json
{
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
    }
  ]
}
```

### For EC2 Instance Profile

Same as above, attach to EC2 instance role.

---

## 🌐 Domain and SSL Setup

### Using AWS Certificate Manager + ALB

1. **Request SSL Certificate**
```bash
aws acm request-certificate \
  --domain-name finops.yourdomain.com \
  --validation-method DNS
```

2. **Configure ALB Listener**
- Add HTTPS listener on port 443
- Attach ACM certificate
- Forward to target group

3. **Update Route53**
- Create A record pointing to ALB
- Enable alias

---

## 📊 Monitoring and Logging

### CloudWatch Logs

```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/finops-agent

# View logs
aws logs tail /ecs/finops-agent --follow
```

### CloudWatch Metrics

Monitor:
- ECS CPU/Memory utilization
- ALB request count
- Bedrock invocation count
- DynamoDB read/write capacity

### Alarms

```bash
# Create CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name finops-agent-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy FinOps Agent

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: finops-agent
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
      
      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster finops-cluster \
            --service finops-agent-service \
            --force-new-deployment
```

---

## 💰 Cost Optimization

### Production Cost Estimates

**Small Deployment (< 100 users/month)**
- ECS Fargate (0.5 vCPU, 1GB): ~$15/month
- ALB: ~$20/month
- Bedrock: ~$20/month
- DynamoDB: ~$5/month
- **Total: ~$60/month**

**Medium Deployment (< 1000 users/month)**
- ECS Fargate (1 vCPU, 2GB): ~$30/month
- ALB: ~$20/month
- Bedrock: ~$100/month
- DynamoDB: ~$10/month
- **Total: ~$160/month**

### Cost Saving Tips

1. Use Fargate Spot for non-production
2. Enable DynamoDB on-demand billing
3. Use CloudFront for static assets
4. Implement request caching
5. Set Bedrock token limits

---

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs <container-id>

# Verify environment variables
docker exec <container-id> env
```

### Can't connect to AWS services
```bash
# Test AWS credentials
aws sts get-caller-identity

# Check security groups
aws ec2 describe-security-groups --group-ids sg-xxx
```

### High latency
- Enable CloudFront
- Use regional Bedrock endpoints
- Implement response caching
- Optimize DynamoDB queries

---

## 📞 Support

For deployment issues:
1. Check CloudWatch logs
2. Review IAM permissions
3. Verify security groups
4. Test AWS service connectivity
5. Open GitHub issue with logs
