# Multi-Agent Gateway Lab Prerequisites

This directory contains the CloudFormation templates and resources needed to deploy the infrastructure for Lab 3: Multi-Agent Gateway.

## Quick Start

The easiest way to deploy all prerequisites is using the provided script:

```bash
cd reinvent
./scripts/prereq.sh
```

This will automatically:
1. Create S3 bucket for Lambda deployment
2. Package and upload Lambda code
3. Deploy Cognito infrastructure
4. Deploy main infrastructure with IAM roles and permissions

## Manual Deployment (Alternative)

If you prefer to deploy manually or need to customize the deployment:

### Step 1: Deploy Infrastructure

```bash
cd reinvent
./scripts/prereq.sh [bucket-name] [infra-stack-name] [cognito-stack-name]
```

**Parameters (all optional):**
- `bucket-name`: S3 bucket prefix (default: multiagent-lab)
- `infra-stack-name`: Infrastructure stack name (default: MultiAgentStackInfra)  
- `cognito-stack-name`: Cognito stack name (default: MultiAgentStackCognito)

**Example with custom names:**
```bash
./scripts/prereq.sh my-custom-bucket MyInfraStack MyCognitoStack
```

## What Gets Created

### Cognito Stack
- User Pool for authentication
- Machine-to-machine client for Gateway access
- Web client for frontend applications
- OAuth scopes and resource servers
- SSM parameters for configuration

### Infrastructure Stack
- **IAM Roles**:
  - `RuntimeAgentCoreRole` - With gateway creation permissions
  - `GatewayAgentCoreRole` - For Gateway Lambda execution
  - `CustomerSupportLambdaRole` - For Lambda function execution

- **DynamoDB Tables**:
  - Warranty information table
  - Customer profile table

- **Lambda Function**:
  - Customer support tools (warranty check, web search)
  - DDGS layer for web search functionality

- **SSM Parameters**:
  - All configuration values needed by the lab
  - IAM role ARNs
  - Lambda function ARN
  - DynamoDB table names

## Verification

After deployment, verify the infrastructure is ready:

```bash
# Check SSM parameters
aws ssm get-parameter --name "/app/customersupport/agentcore/gateway_iam_role"
aws ssm get-parameter --name "/app/customersupport/agentcore/lambda_arn"
aws ssm get-parameter --name "/app/customersupport/agentcore/machine_client_id"

# Check IAM role exists
aws iam get-role --role-name $(aws ssm get-parameter --name "/app/customersupport/agentcore/gateway_iam_role" --query 'Parameter.Value' --output text | cut -d'/' -f2)
```

## Cleanup

To remove all resources:

```bash
# Delete infrastructure stack
aws cloudformation delete-stack --stack-name multiagent-infrastructure-stack

# Delete cognito stack  
aws cloudformation delete-stack --stack-name multiagent-cognito-stack

# Delete S3 bucket (after emptying it)
aws s3 rm s3://your-lambda-deployment-bucket-name --recursive
aws s3 rb s3://your-lambda-deployment-bucket-name
```

## Troubleshooting

### Common Issues

1. **Gateway creation fails with AccessDeniedException**
   - Ensure the infrastructure stack deployed successfully
   - Check that the RuntimeAgentCoreRole has gateway permissions
   - Verify SSM parameters contain correct role ARNs

2. **Lambda function not found**
   - Ensure Lambda code was uploaded to S3 correctly
   - Check the LambdaS3Bucket and LambdaS3Key parameters

3. **Cognito authentication fails**
   - Ensure Cognito stack deployed successfully
   - Check SSM parameters for client IDs and URLs

### Required Permissions

Your AWS user/role needs these permissions to deploy:
- CloudFormation full access
- IAM role creation and management
- Lambda function creation
- DynamoDB table creation
- SSM parameter management
- Cognito User Pool management
- S3 bucket access for Lambda deployment

## Next Steps

Once the infrastructure is deployed successfully, you can run Lab 3: Multi-Agent Gateway. The lab will:

1. Use the pre-created IAM roles for gateway operations
2. Connect to the deployed Lambda function
3. Authenticate using the Cognito setup
4. Create and configure the AgentCore Gateway
5. Test the multi-agent system with shared tools