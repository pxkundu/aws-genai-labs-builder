"""
AWS CDK Stack for Claude Code Workshop
Deploys Lambda, API Gateway, DynamoDB, and S3
"""

from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_iam as iam,
    aws_logs as logs,
    Duration,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct


class ClaudeCodeStack(Stack):
    """CDK Stack for Claude Code Workshop"""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create S3 bucket for code storage
        code_bucket = s3.Bucket(
            self,
            "ClaudeCodeBucket",
            bucket_name=f"claude-code-workshop-{self.account}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=True
        )
        
        # Create DynamoDB table
        code_table = dynamodb.Table(
            self,
            "ClaudeCodeTable",
            table_name="claude-code-results",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            time_to_live_attribute="ttl"
        )
        
        # Add GSI for querying by language
        code_table.add_global_secondary_index(
            index_name="language-index",
            partition_key=dynamodb.Attribute(
                name="language",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="generated_at",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # Create Lambda execution role
        lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ]
        )
        
        # Add Bedrock permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                resources=[
                    "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
                ]
            )
        )
        
        # Add DynamoDB permissions
        code_table.grant_read_write_data(lambda_role)
        
        # Add S3 permissions
        code_bucket.grant_read_write(lambda_role)
        
        # Create Lambda function
        code_generator_lambda = lambda_.Function(
            self,
            "ClaudeCodeGenerator",
            function_name="claude-code-generator",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="lambda_claude_code.lambda_handler",
            code=lambda_.Code.from_asset("../code/examples/aws"),
            role=lambda_role,
            timeout=Duration.seconds(300),
            memory_size=512,
            environment={
                "AWS_REGION": self.region,
                "BEDROCK_MODEL_ID": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "TABLE_NAME": code_table.table_name,
                "BUCKET_NAME": code_bucket.bucket_name
            },
            log_retention=logs.RetentionDays.ONE_WEEK
        )
        
        # Create API Gateway
        api = apigateway.RestApi(
            self,
            "ClaudeCodeAPI",
            rest_api_name="Claude Code API",
            description="API for Claude Code generation",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization"]
            )
        )
        
        # Create /generate endpoint
        generate_resource = api.root.add_resource("generate")
        generate_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(code_generator_lambda)
        )
        
        # Create /health endpoint
        health_resource = api.root.add_resource("health")
        health_resource.add_method("GET")
        
        # Outputs
        CfnOutput(
            self,
            "ApiEndpoint",
            value=api.url,
            description="API Gateway endpoint URL"
        )
        
        CfnOutput(
            self,
            "CodeBucketName",
            value=code_bucket.bucket_name,
            description="S3 bucket for code storage"
        )
        
        CfnOutput(
            self,
            "TableName",
            value=code_table.table_name,
            description="DynamoDB table name"
        )

