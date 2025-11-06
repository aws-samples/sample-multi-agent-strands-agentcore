# Prerequisites Resources Created

**Generated:** 2025-01-07  
**Script:** `./scripts/prereq.sh`  
**Region:** us-east-1  
**Account:** 676206905930

## CloudFormation Stacks

| Stack Name | Status | Purpose |
|------------|--------|---------|
| `MultiAgentStackInfra` | ✅ Deployed | Infrastructure resources (Lambda, S3, IAM) |
| `MultiAgentStackCognito` | ✅ Deployed | Authentication resources (Cognito, OAuth) |

## Cognito Resources

### User Pool
- **Name:** `CustomerSupportGatewayPool`
- **ID:** `us-east-1_vUQSsV593`
- **Purpose:** OAuth authentication for Lab 3 Gateway and Lab 4 Runtime

### Clients
| Client Type | Client ID | Purpose |
|-------------|-----------|---------|
| **Machine Client** | `3uct2nc3l5mga94nv5bc9rbe66` | Agent-to-agent authentication (M2M) |
| **Web Client** | `6vjg1a5agnlodokl76uam7l53n` | Frontend user authentication |

### OAuth Configuration
- **Resource Server:** `default-m2m-resource-server-a9752330`
- **Scope:** `default-m2m-resource-server-a9752330/read`
- **Domain:** `https://us-east-1a9752330.auth.us-east-1.amazoncognito.com`

## Lambda Resources

| Resource | ARN | Purpose |
|----------|-----|---------|
| **Customer Support Lambda** | `arn:aws:lambda:us-east-1:676206905930:function:MultiAgentStackInfra-CustomerSupportLambda-RyhyLXw86Xf8` | Warranty check + web search tools |

## IAM Roles

| Role | ARN | Purpose |
|------|-----|---------|
| **Gateway IAM Role** | `arn:aws:iam::676206905930:role/MultiAgentStackInfra-GatewayAgentCoreRole-eIiKeIslTF91` | AgentCore Gateway permissions |
| **Runtime IAM Role** | `arn:aws:iam::676206905930:role/MultiAgentStackInfra-RuntimeAgentCoreRole-0ph9K8y56nGH` | AgentCore Runtime permissions |

## S3 Resources

| Bucket | Purpose |
|--------|---------|
| `multiagent-lab-676206905930-us-east-1` | Lambda code storage |

## SSM Parameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `/app/reinvent/agentcore/userpool_id` | `us-east-1_vUQSsV593` | Cognito User Pool reference |
| `/app/reinvent/agentcore/machine_client_id` | `3uct2nc3l5mga94nv5bc9rbe66` | M2M client for agents |
| `/app/reinvent/agentcore/web_client_id` | `6vjg1a5agnlodokl76uam7l53n` | Web client for frontend |
| `/app/reinvent/agentcore/cognito_discovery_url` | `https://cognito-idp.us-east-1.amazonaws.com/us-east-1_vUQSsV593/.well-known/openid-configuration` | OAuth discovery endpoint |
| `/app/reinvent/agentcore/cognito_token_url` | `https://us-east-1a9752330.auth.us-east-1.amazoncognito.com/oauth2/token` | OAuth token endpoint |
| `/app/reinvent/agentcore/cognito_auth_url` | `https://us-east-1a9752330.auth.us-east-1.amazoncognito.com/oauth2/authorize` | OAuth authorization endpoint |
| `/app/reinvent/agentcore/cognito_auth_scope` | `default-m2m-resource-server-a9752330/read` | OAuth scope for authentication |
| `/app/reinvent/agentcore/cognito_domain` | `https://us-east-1a9752330.auth.us-east-1.amazoncognito.com` | Cognito hosted domain |
| `/app/reinvent/agentcore/lambda_arn` | `arn:aws:lambda:us-east-1:676206905930:function:MultiAgentStackInfra-CustomerSupportLambda-RyhyLXw86Xf8` | Lambda function reference |
| `/app/reinvent/agentcore/gateway_iam_role` | `arn:aws:iam::676206905930:role/MultiAgentStackInfra-GatewayAgentCoreRole-eIiKeIslTF91` | Gateway IAM role reference |
| `/app/reinvent/agentcore/runtime_iam_role` | `arn:aws:iam::676206905930:role/MultiAgentStackInfra-RuntimeAgentCoreRole-0ph9K8y56nGH` | Runtime IAM role reference |

## Lab Compatibility

| Lab | Status | Notes |
|-----|--------|-------|
| **Lab 1** | ✅ Ready | No prerequisites required |
| **Lab 2** | ✅ Ready | No prerequisites required |
| **Lab 3** | ✅ Ready | Uses `CustomerSupportGatewayPool` |
| **Lab 4** | ⚠️ Naming Issue | Expects `MCPServerPool`, will create duplicates |
| **Lab 5** | ✅ Ready | Uses web client for frontend auth |

## Known Issues

### Lab 4 Duplicate Pool Problem
- **Issue:** Lab 4 expects Cognito pool named `MCPServerPool`
- **Reality:** CloudFormation creates `CustomerSupportGatewayPool`
- **Result:** Lab 4 creates duplicate pools instead of reusing existing ones
- **Impact:** Resource waste and authentication confusion

### Resolution Options
1. **Update CloudFormation:** Change pool name to `MCPServerPool`
2. **Update Lab 4 Code:** Modify to use `CustomerSupportGatewayPool`
3. **Add Name Mapping:** Create compatibility layer between naming conventions

---

*This document tracks all resources created by the prerequisite script for the Re:Invent Multi-Agent Tutorial.*