# AWS CLI Setup Guide

## Installing AWS CLI

### macOS

**Option 1: Using Homebrew (Recommended)**
```bash
brew install awscli
```

**Option 2: Using pip**
```bash
pip install awscli
```

**Option 3: Official Installer**
```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

### Linux

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install awscli
```

**Amazon Linux 2:**
```bash
sudo yum install aws-cli
```

**Using pip:**
```bash
pip install awscli
```

### Windows

**Option 1: MSI Installer**
- Download from: https://awscli.amazonaws.com/AWSCLIV2.msi
- Run the installer

**Option 2: Using pip**
```cmd
pip install awscli
```

### Verify Installation

```bash
aws --version
```

Should output something like: `aws-cli/2.x.x Python/3.x.x Darwin/23.x.x`

---

## Configuring AWS CLI

### Quick Configuration

```bash
aws configure
```

You'll be prompted for:
1. **AWS Access Key ID**: Your access key (from IAM)
2. **AWS Secret Access Key**: Your secret key (from IAM)
3. **Default region**: e.g., `us-east-1`
4. **Default output format**: `json` (recommended)

### Example:
```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

---

## Getting AWS Credentials

### Option 1: Create IAM User (Recommended for Development)

1. **Go to AWS Console** → IAM → Users
2. **Click "Add users"**
3. **Enter username**: e.g., `finops-agent-dev`
4. **Select**: "Programmatic access"
5. **Attach policies**:
   - `AmazonBedrockFullAccess`
   - `AmazonDynamoDBFullAccess`
   - `AmazonAthenaFullAccess`
   - Or create custom policy (see below)
6. **Download credentials** (CSV file)
7. **Run**: `aws configure` and enter the credentials

### Option 2: Use IAM Role (Recommended for Production)

If running on EC2, ECS, or Lambda:
- Attach IAM role to the resource
- No need to configure credentials
- More secure (no keys to manage)

### Custom IAM Policy

Create a policy with minimal permissions:

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
        "dynamodb:CreateTable",
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:DescribeTable"
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
```

---

## Verify AWS Configuration

### Test AWS Credentials

```bash
# Check your identity
aws sts get-caller-identity
```

Should return:
```json
{
    "UserId": "AIDAI...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/finops-agent-dev"
}
```

### Test Bedrock Access

```bash
# List available models
aws bedrock list-foundation-models --region us-east-1
```

### Test DynamoDB Access

```bash
# List tables
aws dynamodb list-tables --region us-east-1
```

---

## Alternative: Using Environment Variables

Instead of `aws configure`, you can set environment variables:

### macOS/Linux

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

Add to `~/.bashrc` or `~/.zshrc` for persistence.

### Windows (CMD)

```cmd
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key
set AWS_DEFAULT_REGION=us-east-1
```

### Windows (PowerShell)

```powershell
$env:AWS_ACCESS_KEY_ID="your_access_key"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key"
$env:AWS_DEFAULT_REGION="us-east-1"
```

---

## Using .env File (Recommended for This Project)

1. **Copy the example file:**
```bash
cp .env.example .env
```

2. **Edit .env with your credentials:**
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
DYNAMODB_TABLE=finops-agent-interactions
```

3. **The app will automatically load these**

**Note:** Never commit `.env` to git (already in `.gitignore`)

---

## AWS Profiles (Multiple Accounts)

If you work with multiple AWS accounts:

### Configure Named Profiles

```bash
# Configure default profile
aws configure

# Configure additional profiles
aws configure --profile work
aws configure --profile personal
```

### Use Specific Profile

```bash
# In commands
aws s3 ls --profile work

# Set for session
export AWS_PROFILE=work

# In .env file
AWS_PROFILE=work
```

---

## Troubleshooting

### Issue 1: "aws: command not found"

**Solution:**
```bash
# Check if installed
which aws

# If not found, install it
brew install awscli  # macOS
# or
pip install awscli
```

### Issue 2: "Unable to locate credentials"

**Solution:**
```bash
# Check credentials file
cat ~/.aws/credentials

# If empty, run:
aws configure
```

### Issue 3: "Access Denied" errors

**Solution:**
- Check IAM permissions
- Verify correct region
- Ensure Bedrock is enabled in your region

```bash
# Check your identity
aws sts get-caller-identity

# Check region
aws configure get region
```

### Issue 4: "Region not specified"

**Solution:**
```bash
# Set default region
aws configure set region us-east-1

# Or use in command
aws s3 ls --region us-east-1
```

### Issue 5: Credentials expired (SSO/Temporary)

**Solution:**
```bash
# Re-authenticate
aws sso login --profile your-profile

# Or get new temporary credentials
```

---

## Security Best Practices

### 1. Never Commit Credentials
- ✅ Use `.env` file (in `.gitignore`)
- ✅ Use IAM roles when possible
- ❌ Don't hardcode in code
- ❌ Don't commit to git

### 2. Use Least Privilege
- Only grant necessary permissions
- Use resource-specific policies
- Regularly review permissions

### 3. Rotate Keys Regularly
```bash
# Create new key in IAM Console
# Update credentials
aws configure
# Delete old key
```

### 4. Enable MFA
- Add MFA to IAM user
- Use MFA for sensitive operations

### 5. Monitor Usage
- Check CloudTrail logs
- Set up billing alerts
- Review IAM access advisor

---

## Quick Start Checklist

- [ ] AWS CLI installed: `aws --version`
- [ ] Credentials configured: `aws configure`
- [ ] Identity verified: `aws sts get-caller-identity`
- [ ] Bedrock access: `aws bedrock list-foundation-models --region us-east-1`
- [ ] DynamoDB access: `aws dynamodb list-tables`
- [ ] Region set: `aws configure get region`
- [ ] `.env` file created and configured

---

## Next Steps

After AWS CLI is configured:

1. **Run setup script:**
```bash
python setup_aws.py
```

2. **Enable Bedrock models:**
- Go to AWS Console → Bedrock → Model Access
- Enable "Anthropic Claude 3 Sonnet"

3. **Run the app:**
```bash
streamlit run streamlit_app.py
```

---

## Additional Resources

- **AWS CLI Documentation**: https://docs.aws.amazon.com/cli/
- **IAM Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **Bedrock Setup**: https://docs.aws.amazon.com/bedrock/
- **DynamoDB Guide**: https://docs.aws.amazon.com/dynamodb/

---

## Getting Help

If you're still having issues:

1. Check AWS CLI version: `aws --version`
2. Check credentials: `cat ~/.aws/credentials`
3. Check config: `cat ~/.aws/config`
4. Test connection: `aws sts get-caller-identity`
5. Open an issue: https://github.com/bgandhi001/finops-genai-agent/issues
