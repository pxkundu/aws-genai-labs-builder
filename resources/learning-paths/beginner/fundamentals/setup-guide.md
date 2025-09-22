# 🚀 Beginner Setup Guide - Get Ready to Learn!

> **Everything you need to start your GenAI journey with AWS**

## 🎯 Welcome to Your Learning Adventure!

Congratulations on taking the first step into the exciting world of AWS GenAI! This guide will help you set up everything you need to have an amazing learning experience. Don't worry - we'll walk you through every step!

## 📋 Prerequisites Checklist

Before we start, let's make sure you have everything you need:

- [ ] 💻 **Computer** - Windows, Mac, or Linux
- [ ] 🌐 **Internet Connection** - Stable broadband recommended
- [ ] 📧 **Email Address** - For creating accounts
- [ ] 📱 **Phone Number** - For account verification
- [ ] 💳 **Credit Card** - For AWS account (we'll use free tier)
- [ ] ⏰ **Time** - 1-2 hours for initial setup
- [ ] 🧠 **Curiosity** - The most important requirement!

## 🏗️ Step 1: Create Your AWS Account

### 🎯 Why AWS?

Amazon Web Services (AWS) is the world's leading cloud platform, and it offers the most comprehensive set of AI services. By learning with AWS, you're learning with industry-standard tools used by companies worldwide.

### 📝 Account Creation Process

#### **Step 1.1: Go to AWS**
1. Open your web browser
2. Go to [aws.amazon.com](https://aws.amazon.com)
3. Click **"Create an AWS Account"** (top right corner)

#### **Step 1.2: Account Information**
Fill in the required information:

```
📧 Email Address: your-email@example.com
👤 Full Name: Your Full Name
🏢 Account Name: MyGenAILearning (or any name you like)
📱 Phone Number: +1-XXX-XXX-XXXX
```

#### **Step 1.3: Account Type**
Choose **"Personal"** for learning purposes

#### **Step 1.4: Payment Information**
- Enter your credit card information
- Don't worry - we'll stay within the free tier limits
- AWS won't charge you without your explicit consent

#### **Step 1.5: Identity Verification**
- Choose **"Text message (SMS)"** for verification
- Enter the verification code you receive

#### **Step 1.6: Support Plan**
Choose **"Basic Support"** (free) - perfect for learning

### ✅ Account Creation Complete!

**Congratulations!** You now have an AWS account. You should see the AWS Management Console.

## 🛠️ Step 2: Set Up Your Development Environment

### 💻 Choose Your Development Setup

You have several options for your development environment:

#### **Option A: Cloud-Based (Recommended for Beginners)**
- **AWS Cloud9** - Integrated development environment in the cloud
- **GitHub Codespaces** - VS Code in the browser
- **Replit** - Online code editor

#### **Option B: Local Development**
- **VS Code** - Popular code editor
- **PyCharm** - Python-focused IDE
- **Jupyter Notebooks** - Interactive development

### 🎯 Recommended: AWS Cloud9 Setup

#### **Step 2.1: Create Cloud9 Environment**
1. In AWS Console, search for **"Cloud9"**
2. Click **"Create environment"**
3. Name: `MyGenAILearning`
4. Description: `Environment for learning AWS GenAI`
5. Click **"Next step"**

#### **Step 2.2: Configure Environment**
- **Instance type**: `t2.micro` (free tier eligible)
- **Platform**: `Ubuntu Server 18.04 LTS`
- **Timeout**: `1 hour`
- Click **"Next step"**

#### **Step 2.3: Review and Create**
- Review your settings
- Click **"Create environment"**
- Wait 2-3 minutes for setup

#### **Step 2.4: Access Your Environment**
- Click **"Open IDE"** when ready
- You'll see a VS Code-like interface in your browser

### 🐍 Install Python and Required Packages

#### **Step 2.5: Check Python Installation**
In your Cloud9 terminal, run:
```bash
python3 --version
```
You should see Python 3.x installed.

#### **Step 2.6: Install Required Packages**
```bash
# Install pip if not already installed
sudo apt update
sudo apt install python3-pip -y

# Install required packages
pip3 install boto3 streamlit pandas numpy matplotlib seaborn plotly
```

#### **Step 2.7: Verify Installation**
```bash
python3 -c "import boto3; print('AWS SDK installed successfully!')"
```

## 🔐 Step 3: Configure AWS Credentials

### 🎯 Why We Need Credentials

AWS services require authentication to ensure security. We'll set up credentials that allow your code to access AWS services.

### 📝 Create IAM User

#### **Step 3.1: Go to IAM**
1. In AWS Console, search for **"IAM"**
2. Click **"Users"** in the left sidebar
3. Click **"Create user"**

#### **Step 3.2: User Details**
- **User name**: `GenAILearningUser`
- **Access type**: Select **"Programmatic access"**
- Click **"Next: Permissions"**

#### **Step 3.3: Attach Policies**
- Click **"Attach existing policies directly"**
- Search for and select:
  - `AmazonBedrockFullAccess`
  - `AmazonComprehendFullAccess`
  - `AmazonRekognitionFullAccess`
  - `AmazonTranscribeFullAccess`
  - `AmazonPollyFullAccess`
- Click **"Next: Tags"** (optional)
- Click **"Next: Review"**

#### **Step 3.4: Create User**
- Review your settings
- Click **"Create user"**
- **IMPORTANT**: Save your Access Key ID and Secret Access Key!

### 🔑 Configure Credentials

#### **Step 3.5: Set Up AWS CLI**
In your Cloud9 terminal:
```bash
# Install AWS CLI
pip3 install awscli

# Configure credentials
aws configure
```

When prompted, enter:
```
AWS Access Key ID: [Your Access Key ID]
AWS Secret Access Key: [Your Secret Access Key]
Default region name: us-east-1
Default output format: json
```

#### **Step 3.6: Test Configuration**
```bash
# Test your configuration
aws sts get-caller-identity
```

You should see your user information.

## 🎨 Step 4: Enable Required AWS Services

### 🚀 Enable Amazon Bedrock

#### **Step 4.1: Access Bedrock**
1. In AWS Console, search for **"Bedrock"**
2. Click **"Get started"** or **"Enable Bedrock"**

#### **Step 4.2: Model Access**
- Click **"Request model access"**
- Select **"Claude 3.5 Sonnet"** and **"Claude 3 Haiku"**
- Click **"Request access"**
- Wait for approval (usually instant)

### 🔧 Enable Other AI Services

#### **Step 4.3: Enable Comprehend**
1. Search for **"Comprehend"**
2. Click **"Get started"**
3. No additional setup required

#### **Step 4.4: Enable Rekognition**
1. Search for **"Rekognition"**
2. Click **"Get started"**
3. No additional setup required

#### **Step 4.5: Enable Transcribe**
1. Search for **"Transcribe"**
2. Click **"Get started"**
3. No additional setup required

#### **Step 4.6: Enable Polly**
1. Search for **"Polly"**
2. Click **"Get started"**
3. No additional setup required

## 🧪 Step 5: Test Your Setup

### 🎯 Create Your First Test

#### **Step 5.1: Create Test File**
In Cloud9, create a new file called `test_setup.py`:

```python
import boto3
import json

def test_aws_services():
    """Test if all AWS services are accessible"""
    
    print("🧪 Testing AWS Services Setup...")
    print("=" * 40)
    
    # Test Bedrock
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        print("✅ Amazon Bedrock: Connected")
    except Exception as e:
        print(f"❌ Amazon Bedrock: Error - {e}")
    
    # Test Comprehend
    try:
        comprehend = boto3.client('comprehend', region_name='us-east-1')
        print("✅ Amazon Comprehend: Connected")
    except Exception as e:
        print(f"❌ Amazon Comprehend: Error - {e}")
    
    # Test Rekognition
    try:
        rekognition = boto3.client('rekognition', region_name='us-east-1')
        print("✅ Amazon Rekognition: Connected")
    except Exception as e:
        print(f"❌ Amazon Rekognition: Error - {e}")
    
    # Test Transcribe
    try:
        transcribe = boto3.client('transcribe', region_name='us-east-1')
        print("✅ Amazon Transcribe: Connected")
    except Exception as e:
        print(f"❌ Amazon Transcribe: Error - {e}")
    
    # Test Polly
    try:
        polly = boto3.client('polly', region_name='us-east-1')
        print("✅ Amazon Polly: Connected")
    except Exception as e:
        print(f"❌ Amazon Polly: Error - {e}")
    
    print("=" * 40)
    print("🎉 Setup test complete!")

if __name__ == "__main__":
    test_aws_services()
```

#### **Step 5.2: Run the Test**
```bash
python3 test_setup.py
```

You should see all services showing as connected.

### 🎨 Test Bedrock with a Simple Example

#### **Step 5.3: Create Bedrock Test**
Create a file called `test_bedrock.py`:

```python
import boto3
import json

def test_bedrock():
    """Test Bedrock with a simple prompt"""
    
    print("🤖 Testing Amazon Bedrock...")
    
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Simple prompt
        prompt = "Hello! Can you tell me what you are?"
        
        # Call Claude model
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 100,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        # Get response
        result = json.loads(response['body'].read())
        ai_response = result['content'][0]['text']
        
        print("✅ Bedrock Response:")
        print(f"🤖 AI: {ai_response}")
        
    except Exception as e:
        print(f"❌ Error testing Bedrock: {e}")

if __name__ == "__main__":
    test_bedrock()
```

#### **Step 5.4: Run Bedrock Test**
```bash
python3 test_bedrock.py
```

You should see a response from Claude!

## 🎯 Step 6: Set Up Your Learning Environment

### 📁 Create Project Structure

#### **Step 6.1: Create Learning Directory**
```bash
# Create main learning directory
mkdir -p ~/genai-learning
cd ~/genai-learning

# Create subdirectories
mkdir -p projects
mkdir -p notes
mkdir -p resources
mkdir -p experiments
```

#### **Step 6.2: Create Learning Journal**
```bash
# Create a learning journal
touch ~/genai-learning/notes/learning_journal.md
```

Add this to your journal:
```markdown
# My GenAI Learning Journal

## Day 1: Setup Complete! 🎉
- ✅ AWS Account created
- ✅ Development environment ready
- ✅ All services tested and working
- ✅ Ready to start learning!

## Goals for This Week:
- [ ] Complete GenAI Fundamentals module
- [ ] Build first AI chatbot
- [ ] Learn about AWS AI services

## Notes:
- Everything is working perfectly!
- Excited to start building AI applications!
```

### 🎮 Set Up Interactive Learning

#### **Step 6.3: Install Jupyter Notebooks**
```bash
# Install Jupyter for interactive learning
pip3 install jupyter notebook

# Start Jupyter
jupyter notebook --ip=0.0.0.0 --port=8080 --no-browser --allow-root
```

#### **Step 6.4: Access Jupyter**
1. In Cloud9, click **"Preview"** → **"Preview Running Application"**
2. Add `:8080` to the URL
3. You'll see the Jupyter interface

## 🎉 Step 7: You're Ready to Learn!

### 🎯 What You've Accomplished

- ✅ **AWS Account** - Full access to AWS services
- ✅ **Development Environment** - Cloud9 IDE ready
- ✅ **AWS Credentials** - Secure access configured
- ✅ **AI Services** - All services enabled and tested
- ✅ **Learning Environment** - Organized and ready
- ✅ **First AI Interaction** - You've already talked to AI!

### 🚀 Next Steps

1. **📚 Start with Fundamentals** - Begin your learning journey
2. **🎮 Try Interactive Content** - Make learning fun
3. **🛠️ Build Your First Project** - Apply what you learn
4. **🤝 Join the Community** - Learn with others

### 🎯 Quick Reference

#### **Important Commands**
```bash
# Test AWS connection
aws sts get-caller-identity

# Run Python scripts
python3 your_script.py

# Start Jupyter
jupyter notebook --ip=0.0.0.0 --port=8080 --no-browser --allow-root

# Check Python packages
pip3 list
```

#### **Important URLs**
- **AWS Console**: [console.aws.amazon.com](https://console.aws.amazon.com)
- **Cloud9 IDE**: Access from AWS Console
- **Jupyter Notebooks**: `http://localhost:8080` (in Cloud9 preview)

#### **Important Files**
- **Learning Journal**: `~/genai-learning/notes/learning_journal.md`
- **Test Scripts**: `test_setup.py`, `test_bedrock.py`
- **Projects**: `~/genai-learning/projects/`

## 🆘 Troubleshooting

### ❌ Common Issues and Solutions

#### **Issue: "Access Denied" when calling AWS services**
**Solution:**
```bash
# Check your credentials
aws sts get-caller-identity

# If error, reconfigure
aws configure
```

#### **Issue: "Model access not granted" for Bedrock**
**Solution:**
1. Go to AWS Console → Bedrock
2. Click "Model access"
3. Request access to Claude models
4. Wait for approval

#### **Issue: "Region not supported"**
**Solution:**
```bash
# Use us-east-1 region
aws configure
# Enter: us-east-1
```

#### **Issue: "Package not found"**
**Solution:**
```bash
# Install missing package
pip3 install package_name

# Or install all at once
pip3 install boto3 streamlit pandas numpy matplotlib seaborn plotly
```

### 🆘 Getting Help

If you encounter issues:

1. **📚 Check the Documentation** - AWS has excellent docs
2. **🤝 Ask the Community** - Join our learning community
3. **🔍 Search Online** - Many solutions are available
4. **👨‍🏫 Contact Support** - We're here to help!

## 🎉 Congratulations!

**You've successfully set up your AWS GenAI learning environment!** 

You now have:
- 🏗️ **A complete development environment**
- ☁️ **Access to all AWS AI services**
- 🛠️ **All the tools you need to learn**
- 🎯 **A clear path forward**

**Ready to start your GenAI journey? Let's begin! 🚀**

---

## 🔗 Quick Links

- **[Start Learning Fundamentals →](./README.md)**
- **[Try Interactive Content →](../interactive-content/)**
- **[Join the Community →](../quizzes/)**
- **[Build Your First Project →](../hands-on-labs/)**

---

**Remember: Every expert was once a beginner. You've taken the first step - now let's make it count! 💪✨**
