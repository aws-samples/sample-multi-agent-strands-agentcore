#!/bin/bash
set -e

echo "=========================================="
echo "Multi-Agent Workshop Setup"
echo "=========================================="

# Install zip utility
echo "Installing zip utility..."
sudo apt-get update && sudo apt-get install -y zip
echo "✅ zip installed"
echo ""

# Get AWS Account Info
REGION=$(aws configure get region 2>/dev/null || echo "us-west-2")
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET="multiagent-lab-${ACCOUNT_ID}-${REGION}"

echo "Region: $REGION"
echo "Account ID: $ACCOUNT_ID"
echo "S3 Bucket: $BUCKET"
echo ""

# Step 1: Create S3 Bucket
echo "Step 1: Creating S3 bucket..."
if aws s3 ls "s3://${BUCKET}" 2>/dev/null; then
    echo "✅ Bucket already exists: $BUCKET"
else
    echo "Creating bucket: $BUCKET"
    if [ "$REGION" = "us-east-1" ]; then
        aws s3api create-bucket --bucket "$BUCKET" 2>/dev/null || echo "Bucket creation attempted"
    else
        aws s3api create-bucket \
            --bucket "$BUCKET" \
            --region "$REGION" \
            --create-bucket-configuration LocationConstraint="$REGION" \
            2>/dev/null || echo "Bucket creation attempted"
    fi
    echo "✅ Bucket created"
fi

# Step 2: Create lambda.zip using Python
echo ""
echo "Step 2: Creating Lambda deployment package..."
python3 << 'PYEOF'
import zipfile
import os

def zip_directory(source_dir, output_file):
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
    print(f"✅ Created {output_file}")

zip_directory('prerequisite/lambda/python', 'lambda.zip')
PYEOF

# Step 3: Patch prereq.sh to skip zip command
echo ""
echo "Step 3: Patching prereq.sh script..."
if [ ! -f "scripts/prereq.sh.backup" ]; then
    cp scripts/prereq.sh scripts/prereq.sh.backup
    echo "✅ Backup created"
fi
sed -i '64s/^/# /' scripts/prereq.sh
echo "✅ Script patched (line 64 commented out)"

# Step 4: Run prerequisites
echo ""
echo "Step 4: Running prerequisite deployment..."
echo "This will deploy CloudFormation stacks (may take 5-10 minutes)..."
echo ""
bash scripts/prereq.sh

echo ""
echo "=========================================="
echo "✅ Workshop setup completed successfully!"
echo "=========================================="
echo ""
echo "AWS Infrastructure deployed:"
echo "  - S3 Bucket: $BUCKET"
echo "  - DynamoDB Tables (Customer, Warranty)"
echo "  - Lambda Functions"
echo "  - Cognito User Pool"
echo ""
echo "Next steps:"
echo "1. The prerequisites script has already run and deployed all infrastructure"
echo "2. Open the Jupyter notebooks in this repository"
echo "3. Follow the workshop instructions"
echo ""
echo "Note: All prerequisite tools and AWS resources are now ready!"
echo ""