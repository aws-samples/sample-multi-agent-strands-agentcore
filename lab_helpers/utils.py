import base64
import hashlib
import hmac
import json
import os
from typing import Any, Dict

import boto3
from boto3.session import Session

sts_client = boto3.client("sts")

# Get AWS account details
REGION = boto3.session.Session().region_name

username = "testuser@example.com"
secret_name = "customer_support_agent"

role_name = f"AgentCoreRole-{REGION}"
policy_name = f"AgentCorePolicy-{REGION}"


def get_ssm_parameter(name: str, with_decryption: bool = True) -> str:
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name=name, WithDecryption=with_decryption)
    return response["Parameter"]["Value"]


def put_ssm_parameter(
    name: str, value: str, parameter_type: str = "String", with_encryption: bool = False
) -> None:
    ssm = boto3.client("ssm")
    put_params = {
        "Name": name,
        "Value": value,
        "Type": parameter_type,
        "Overwrite": True,
    }
    if with_encryption:
        put_params["Type"] = "SecureString"
    ssm.put_parameter(**put_params)


def get_aws_account_id() -> str:
    sts = boto3.client("sts")
    return sts.get_caller_identity()["Account"]


def get_cognito_client_secret() -> str:
    client = boto3.client("cognito-idp")
    response = client.describe_user_pool_client(
        UserPoolId=get_ssm_parameter("/app/reinvent/agentcore/userpool_id"),
        ClientId=get_ssm_parameter("/app/reinvent/agentcore/machine_client_id"),
    )
    return response["UserPoolClient"]["ClientSecret"]


def setup_cognito_user_pool():
    boto_session = Session()
    region = boto_session.region_name
    # Initialize Cognito client
    cognito_client = boto3.client("cognito-idp", region_name=region)
    try:
        # Create User Pool
        user_pool_response = cognito_client.create_user_pool(
            PoolName="MCPServerPool", Policies={"PasswordPolicy": {"MinimumLength": 8}}
        )
        pool_id = user_pool_response["UserPool"]["Id"]
        # Create App Client
        app_client_response = cognito_client.create_user_pool_client(
            UserPoolId=pool_id,
            ClientName="MCPServerPoolClient",
            GenerateSecret=True,
            ExplicitAuthFlows=[
                "ALLOW_USER_PASSWORD_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
                "ALLOW_USER_SRP_AUTH",
            ],
        )
        print(app_client_response["UserPoolClient"])
        client_id = app_client_response["UserPoolClient"]["ClientId"]
        client_secret = app_client_response["UserPoolClient"]["ClientSecret"]

        # Create User
        cognito_client.admin_create_user(
            UserPoolId=pool_id,
            Username=username,
            TemporaryPassword="Temp123!",
            MessageAction="SUPPRESS",
        )

        # Set Permanent Password
        cognito_client.admin_set_user_password(
            UserPoolId=pool_id,
            Username=username,
            Password="MyPassword123!",
            Permanent=True,
        )

        app_client_id = client_id
        key = client_secret
        message = bytes(username + app_client_id, "utf-8")
        key = bytes(key, "utf-8")
        secret_hash = base64.b64encode(
            hmac.new(key, message, digestmod=hashlib.sha256).digest()
        ).decode()

        # Authenticate User and get Access Token
        auth_response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": "testuser",
                "PASSWORD": "MyPassword123!",
                "SECRET_HASH": secret_hash,
            },
        )
        bearer_token = auth_response["AuthenticationResult"]["AccessToken"]
        # Output the required values
        print(f"Pool id: {pool_id}")
        print(
            f"Discovery URL: https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/openid-configuration"
        )
        print(f"Client ID: {client_id}")
        print(f"Bearer Token: {bearer_token}")

        # Return values if needed for further processing
        cognito_config = {
            "UserPoolId": pool_id,
            "ClientId": client_id,
            "ClientSecret": client_secret,
            "SecretHash": secret_hash,
            "Bearer Token": bearer_token,
            "discovery_url": f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/openid-configuration",
        }

        return cognito_config
    except Exception as e:
        print(f"Error: {e}")
        return None


def setup_or_reuse_cognito_user_pool():
    """
    Smart Cognito setup that reuses existing pools instead of creating new ones.
    
    This function:
    1. Checks if a Cognito pool already exists (from SSM parameters)
    2. If exists and valid, reuses it and gets a fresh token
    3. If not exists or invalid, falls back to creating a new pool
    
    Returns the same format as setup_cognito_user_pool() for compatibility.
    """
    import base64
    import hashlib
    import hmac
    
    boto_session = Session()
    region = boto_session.region_name
    cognito_client = boto3.client("cognito-idp", region_name=region)
    
    try:
        print("🔍 Checking for existing Cognito pool...")
        
        # Try to get existing pool configuration from SSM
        existing_pool_id = get_ssm_parameter("/app/reinvent/agentcore/userpool_id")
        existing_client_id = get_ssm_parameter("/app/reinvent/agentcore/machine_client_id")
        existing_discovery_url = get_ssm_parameter("/app/reinvent/agentcore/cognito_discovery_url")
        
        print(f"✅ Found existing pool: {existing_pool_id}")
        print(f"✅ Found existing client: {existing_client_id}")
        
        # Verify the pool still exists in AWS
        pool_info = cognito_client.describe_user_pool(UserPoolId=existing_pool_id)
        client_info = cognito_client.describe_user_pool_client(
            UserPoolId=existing_pool_id,
            ClientId=existing_client_id
        )
        
        print(f"✅ Pool verified: {pool_info['UserPool']['Name']}")
        print(f"✅ Client verified: {client_info['UserPoolClient']['ClientName']}")
        
        # Get the client secret for the existing client
        client_secret = get_cognito_client_secret()
        print("✅ Retrieved client secret")
        
        # Generate secret hash for authentication
        message = bytes(username + existing_client_id, "utf-8")
        key = bytes(client_secret, "utf-8")
        secret_hash = base64.b64encode(
            hmac.new(key, message, digestmod=hashlib.sha256).digest()
        ).decode()
        
        # Check if USER_PASSWORD_AUTH is enabled for this client
        explicit_auth_flows = client_info['UserPoolClient'].get('ExplicitAuthFlows', [])
        
        if 'ALLOW_USER_PASSWORD_AUTH' not in explicit_auth_flows:
            print(f"⚠️  Client doesn't support USER_PASSWORD_AUTH flow")
            print(f"   Current flows: {explicit_auth_flows}")
            print("🔧 Updating client to enable USER_PASSWORD_AUTH...")
            
            # Update the client to enable the required auth flow
            cognito_client.update_user_pool_client(
                UserPoolId=existing_pool_id,
                ClientId=existing_client_id,
                ExplicitAuthFlows=[
                    "ALLOW_USER_PASSWORD_AUTH",
                    "ALLOW_USER_SRP_AUTH", 
                    "ALLOW_REFRESH_TOKEN_AUTH"
                ] + explicit_auth_flows  # Keep existing flows too
            )
            print("✅ Client updated with USER_PASSWORD_AUTH flow")
        
        # Check if test user exists, create if missing
        try:
            cognito_client.admin_get_user(
                UserPoolId=existing_pool_id,
                Username=username
            )
            print("✅ Test user already exists")
        except cognito_client.exceptions.UserNotFoundException:
            print("🔧 Creating test user...")
            
            # Create User
            cognito_client.admin_create_user(
                UserPoolId=existing_pool_id,
                Username=username,
                TemporaryPassword="Temp123!",
                MessageAction="SUPPRESS",
            )
            
            # Set Permanent Password
            cognito_client.admin_set_user_password(
                UserPoolId=existing_pool_id,
                Username=username,
                Password="MyPassword123!",
                Permanent=True,
            )
            print("✅ Test user created")
        
        # Get fresh access token from existing pool
        auth_response = cognito_client.initiate_auth(
            ClientId=existing_client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": "MyPassword123!",
                "SECRET_HASH": secret_hash,
            },
        )
        
        bearer_token = auth_response["AuthenticationResult"]["AccessToken"]
        
        print(f"✅ Got fresh token from existing pool")
        print(f"Pool id: {existing_pool_id}")
        print(f"Discovery URL: {existing_discovery_url}")
        print(f"Client ID: {existing_client_id}")
        print(f"Bearer Token: {bearer_token}")
        
        # Return in same format as setup_cognito_user_pool()
        cognito_config = {
            "UserPoolId": existing_pool_id,
            "ClientId": existing_client_id,
            "ClientSecret": client_secret,
            "SecretHash": secret_hash,
            "Bearer Token": bearer_token,
            "discovery_url": existing_discovery_url,
        }
        
        return cognito_config
        
    except Exception as e:
        print(f"⚠️  Existing pool not found or invalid: {e}")
        print("❌ Cannot proceed without valid Cognito pool from prerequisite script")
        print("💡 Please run: ./scripts/prereq.sh to create required infrastructure")
        
        # Commented out to prevent duplicate pool creation
        # return setup_cognito_user_pool()
        raise Exception(f"No valid Cognito pool found. Run prerequisite script first: {e}")


def create_agentcore_runtime_execution_role(agent_name=None):
    iam = boto3.client("iam")
    boto_session = Session()
    region = boto_session.region_name
    account_id = get_aws_account_id()

    # Use agent-specific role names if agent_name is provided
    if agent_name:
        # Keep role names under 64 characters (AWS limit)
        role_name_specific = f"AgentCoreRole-{agent_name}-{region}"
        policy_name_specific = f"AgentCorePolicy-{agent_name}-{region}"
    else:
        role_name_specific = role_name
        policy_name_specific = policy_name

    # Trust relationship policy
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AssumeRolePolicy",
                "Effect": "Allow",
                "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {"aws:SourceAccount": account_id},
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock-agentcore:{region}:{account_id}:*"
                    },
                },
            }
        ],
    }

    # IAM policy document
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "ECRImageAccess",
                "Effect": "Allow",
                "Action": ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"],
                "Resource": [f"arn:aws:ecr:{region}:{account_id}:repository/*"],
            },
            {
                "Effect": "Allow",
                "Action": ["logs:DescribeLogStreams", "logs:CreateLogGroup"],
                "Resource": [
                    f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*"
                ],
            },
            {
                "Effect": "Allow",
                "Action": ["logs:DescribeLogGroups"],
                "Resource": [f"arn:aws:logs:{region}:{account_id}:log-group:*"],
            },
            {
                "Effect": "Allow",
                "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
                "Resource": [
                    f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"
                ],
            },
            {
                "Sid": "ECRTokenAccess",
                "Effect": "Allow",
                "Action": ["ecr:GetAuthorizationToken"],
                "Resource": "*",
            },
            {
                "Effect": "Allow",
                "Action": [
                    "xray:PutTraceSegments",
                    "xray:PutTelemetryRecords",
                    "xray:GetSamplingRules",
                    "xray:GetSamplingTargets",
                ],
                "Resource": ["*"],
            },
            {
                "Effect": "Allow",
                "Resource": "*",
                "Action": "cloudwatch:PutMetricData",
                "Condition": {
                    "StringEquals": {"cloudwatch:namespace": "bedrock-agentcore"}
                },
            },
            {
                "Sid": "GetAgentAccessToken",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:GetWorkloadAccessToken",
                    "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
                    "bedrock-agentcore:GetWorkloadAccessTokenForUserId",
                ],
                "Resource": [
                    f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default",
                    f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default/workload-identity/orchestrator_agent-*",
                    f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default/workload-identity/customer_support_agent-*",
                    f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default/workload-identity/knowledge_base_agent-*",
                ],
            },
            {
                "Sid": "BedrockModelInvocation",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                    "bedrock:ApplyGuardrail",
                    "bedrock:Retrieve",
                ],
                "Resource": [
                    "arn:aws:bedrock:*::foundation-model/*",
                    f"arn:aws:bedrock:{region}:{account_id}:*",
                ],
            },
            {
                "Sid": "AllowAgentToUseMemory",
                "Effect": "Allow",
                "Action": [
                    "bedrock-agentcore:CreateEvent",
                    "bedrock-agentcore:GetMemoryRecord",
                    "bedrock-agentcore:GetMemory",
                    "bedrock-agentcore:RetrieveMemoryRecords",
                    "bedrock-agentcore:ListMemoryRecords",
                ],
                "Resource": [f"arn:aws:bedrock-agentcore:{region}:{account_id}:*"],
            },
            {
                "Sid": "GetMemoryId",
                "Effect": "Allow",
                "Action": ["ssm:GetParameter"],
                "Resource": [f"arn:aws:ssm:{region}:{account_id}:parameter/app/*"],
            },
        ],
    }

    try:
        # Check if role already exists
        try:
            existing_role = iam.get_role(RoleName=role_name_specific)
            print(f"ℹ️ Role {role_name_specific} already exists")
            print(f"Role ARN: {existing_role['Role']['Arn']}")
            return existing_role["Role"]["Arn"]
        except iam.exceptions.NoSuchEntityException:
            pass

        # Create IAM role
        role_response = iam.create_role(
            RoleName=role_name_specific,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=f"IAM role for Amazon Bedrock AgentCore {agent_name or 'runtime'} with required permissions",
        )

        print(f"✅ Created IAM role: {role_name_specific}")
        print(f"Role ARN: {role_response['Role']['Arn']}")

        # Check if policy already exists
        policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name_specific}"

        try:
            iam.get_policy(PolicyArn=policy_arn)
            print(f"ℹ️ Policy {policy_name_specific} already exists")
        except iam.exceptions.NoSuchEntityException:
            # Create policy
            policy_response = iam.create_policy(
                PolicyName=policy_name_specific,
                PolicyDocument=json.dumps(policy_document),
                Description=f"Policy for Amazon Bedrock AgentCore {agent_name or 'runtime'} permissions",
            )
            print(f"✅ Created policy: {policy_name_specific}")
            policy_arn = policy_response["Policy"]["Arn"]

        # Attach policy to role
        try:
            iam.attach_role_policy(RoleName=role_name_specific, PolicyArn=policy_arn)
            print("✅ Attached policy to role")
        except Exception as e:
            if "already attached" in str(e).lower():
                print("ℹ️ Policy already attached to role")
            else:
                raise

        print(f"Policy ARN: {policy_arn}")

        # Store in SSM with agent-specific parameter name if provided
        ssm_param_name = f"/app/reinvent/agentcore/runtime_execution_role_arn"
        if agent_name:
            ssm_param_name = f"/app/reinvent/agentcore/{agent_name}_runtime_execution_role_arn"
        
        put_ssm_parameter(ssm_param_name, role_response["Role"]["Arn"])
        return role_response["Role"]["Arn"]

    except Exception as e:
        print(f"❌ Error creating IAM role: {str(e)}")
        print(f"💡 Tip: If role name is too long, try using a shorter agent name")
        raise Exception(f"Failed to create IAM role for agent '{agent_name}': {str(e)}")


def reauthenticate_user(client_id, client_secret):
    """Reauthenticate user and get fresh access token"""
    boto_session = Session()
    region = boto_session.region_name
    # Initialize Cognito client
    cognito_client = boto3.client("cognito-idp", region_name=region)
    
    # Create secret hash
    message = bytes(username + client_id, "utf-8")
    key = bytes(client_secret, "utf-8")
    secret_hash = base64.b64encode(
        hmac.new(key, message, digestmod=hashlib.sha256).digest()
    ).decode()

    # Authenticate User and get Access Token
    auth_response = cognito_client.initiate_auth(
        ClientId=client_id,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={
            "USERNAME": username,
            "PASSWORD": "MyPassword123!",
            "SECRET_HASH": secret_hash,
        },
    )
    bearer_token = auth_response["AuthenticationResult"]["AccessToken"]
    return bearer_token