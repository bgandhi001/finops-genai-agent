# How to Get AWS Credentials

## Quick Guide: Get Your AWS Access Keys

### Step 1: Sign in to AWS Console
Go to: https://console.aws.amazon.com/

### Step 2: Navigate to IAM
1. In the search bar at the top, type **"IAM"**
2. Click on **"IAM"** (Identity and Access Management)

### Step 3: Create a New User
1. Click **"Users"** in the left sidebar
2. Click **"Add users"** button (top right)
3. Enter username: `finops-agent-dev`
4. Click **"Next"**

### Step 4: Set Permissions
1. Select **"Attach policies directly"**
2. Search and check these policies:
   - ✅ `AmazonBedrockFullAccess`
   - ✅ `AmazonDynamoDBFullAccess`
   - ✅ `AmazonAthenaFullAccess`
3. Click **"Next"**
4. Click **"Create user"**

### Step 5: Create Access Key
1. Click on the user you just created (`finops-agent-dev`)
2. Click **"Security credentials"** tab
3. Scroll down to **"Access keys"**
4. Click **"Create access key"**
5. Select **"Command Line Interface (CLI)"**
6. Check the confirmation box
7. Click **"Next"**
8. (Optional) Add description: "FinOps GenAI Agent"
9. Click **"Create access key"**

### Step 6: Save Your Credentials
You'll see:
- **Access key ID**: `AKIAIOSFODNN7EXAMPLE`
- **Secret access key**: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

⚠️ **IMPORTANT**: Copy these now! You won't be able to see the secret key again.

**Option A: Download CSV**
- Click **"Download .csv file"**
- Save it securely

**Option B: Copy manually**
- Copy both keys to a secure location

### Step 7: Add to .env File

1. **Open .env file:**
```bash
# macOS/Linux
nano .env

# Windows
notepad .env
```

2. **Replace the placeholder values:**
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE  # Replace with your actual key
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY  # Replace with your actual secret
DYNAMODB_TABLE=finops-agent-interactions
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

3. **Save the file**

### Step 8: Verify Setup

```bash
python setup_aws.py
```

You should see:
```
✅ AWS Credentials configured
   Account: 123456789012
   User/Role: arn:aws:iam::123456789012:user/finops-agent-dev
```

---

## Alternative: Use Existing Credentials

If you already have AWS credentials:

### Find Your Existing Keys

**Option 1: Check AWS Console**
1. Go to IAM → Users → Your User
2. Security credentials tab
3. Access keys section
4. If you have an existing key, you can use it
5. If not, create a new one (see Step 5 above)

**Option 2: Check Local Files**
```bash
# macOS/Linux
cat ~/.aws/credentials

# Windows
type %USERPROFILE%\.aws\credentials
```

If you see credentials there, copy them to your `.env` file.

---

## Security Best Practices

### ✅ DO:
- Store credentials in `.env` file (already in `.gitignore`)
- Use IAM user with minimal permissions
- Rotate keys regularly (every 90 days)
- Delete unused access keys

### ❌ DON'T:
- Commit `.env` to git
- Share credentials in chat/email
- Use root account credentials
- Hardcode credentials in code

---

## Troubleshooting

### "Access Denied" Errors

**Problem**: User doesn't have required permissions

**Solution**: Add these policies to your IAM user:
1. Go to IAM → Users → Your User
2. Click "Add permissions"
3. Attach policies:
   - `AmazonBedrockFullAccess`
   - `AmazonDynamoDBFullAccess`

### "Invalid Access Key"

**Problem**: Wrong credentials or typo

**Solution**:
1. Double-check your `.env` file
2. Make sure there are no extra spaces
3. Verify keys in AWS Console (IAM → Users → Security credentials)

### "Region Not Available"

**Problem**: Bedrock not available in your region

**Solution**: Change region in `.env`:
```bash
AWS_REGION=us-east-1  # Bedrock is available here
```

Bedrock is available in:
- `us-east-1` (N. Virginia)
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)
- `ap-southeast-1` (Singapore)

---

## Quick Reference

### .env File Template
```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
DYNAMODB_TABLE=finops-agent-interactions
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

### Test Commands
```bash
# Test setup
python setup_aws.py

# Run the app
streamlit run streamlit_app.py
```

---

## Need More Help?

- **Detailed AWS CLI Guide**: [AWS_CLI_SETUP.md](AWS_CLI_SETUP.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Full Documentation**: [README_STREAMLIT.md](README_STREAMLIT.md)
- **AWS IAM Documentation**: https://docs.aws.amazon.com/IAM/

---

## Video Tutorial (Coming Soon)

We're working on a video walkthrough. In the meantime, follow the steps above or open an issue if you need help!
