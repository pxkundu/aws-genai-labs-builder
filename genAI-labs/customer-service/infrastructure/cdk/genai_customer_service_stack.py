"""
AWS CDK Stack for GenAI Customer Service
"""

from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_iam as iam,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_elasticache as elasticache,
    aws_opensearch as opensearch,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    aws_sns as sns,
    aws_sqs as sqs,
    aws_kms as kms,
    Duration,
    RemovalPolicy,
    CfnOutput,
)


class GenaiCustomerServiceStack(Stack):
    """GenAI Customer Service Infrastructure Stack"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create KMS key for encryption
        self.kms_key = kms.Key(
            self,
            "GenaiCustomerServiceKmsKey",
            description="KMS key for GenAI Customer Service encryption",
            enable_key_rotation=True,
        )

        # Create VPC
        self.vpc = ec2.Vpc(
            self,
            "GenaiCustomerServiceVpc",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
        )

        # Create S3 bucket for file storage
        self.s3_bucket = s3.Bucket(
            self,
            "GenaiCustomerServiceBucket",
            bucket_name=f"genai-customer-service-{self.account}-{self.region}",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.kms_key,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Create DynamoDB tables
        self.conversations_table = dynamodb.Table(
            self,
            "ConversationsTable",
            table_name="genai-cs-conversations",
            partition_key=dynamodb.Attribute(
                name="customer_id", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="session_id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.CUSTOMER_MANAGED,
            encryption_key=self.kms_key,
            point_in_time_recovery=True,
        )

        self.customers_table = dynamodb.Table(
            self,
            "CustomersTable",
            table_name="genai-cs-customers",
            partition_key=dynamodb.Attribute(
                name="customer_id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.CUSTOMER_MANAGED,
            encryption_key=self.kms_key,
            point_in_time_recovery=True,
        )

        self.knowledge_table = dynamodb.Table(
            self,
            "KnowledgeTable",
            table_name="genai-cs-knowledge",
            partition_key=dynamodb.Attribute(
                name="article_id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            encryption=dynamodb.TableEncryption.CUSTOMER_MANAGED,
            encryption_key=self.kms_key,
            point_in_time_recovery=True,
        )

        # Create ElastiCache Redis cluster
        self.redis_subnet_group = elasticache.CfnSubnetGroup(
            self,
            "RedisSubnetGroup",
            description="Subnet group for Redis cluster",
            subnet_ids=[subnet.subnet_id for subnet in self.vpc.private_subnets],
        )

        self.redis_cluster = elasticache.CfnCacheCluster(
            self,
            "RedisCluster",
            cache_node_type="cache.t3.micro",
            engine="redis",
            num_cache_nodes=1,
            cache_subnet_group_name=self.redis_subnet_group.ref,
            vpc_security_group_ids=[self._create_redis_security_group().security_group_id],
        )

        # Create OpenSearch domain
        self.opensearch_domain = opensearch.Domain(
            self,
            "OpenSearchDomain",
            domain_name="genai-cs-knowledge-base",
            version=opensearch.EngineVersion.OPENSEARCH_2_3,
            capacity=opensearch.CapacityConfig(
                data_nodes=1,
                data_node_instance_type="t3.small.search",
            ),
            ebs=opensearch.EbsOptions(
                volume_size=20,
                volume_type=ec2.EbsDeviceVolumeType.GP3,
            ),
            encryption_at_rest=opensearch.EncryptionAtRestOptions(
                enabled=True,
                kms_key=self.kms_key,
            ),
            node_to_node_encryption=opensearch.NodeToNodeEncryptionOptions(
                enabled=True,
            ),
            domain_endpoint_options=opensearch.DomainEndpointOptions(
                enforce_https=True,
            ),
            vpc=self.vpc,
            vpc_subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)],
            security_groups=[self._create_opensearch_security_group()],
        )

        # Create Lambda functions
        self.api_lambda = self._create_api_lambda()
        self.ai_processing_lambda = self._create_ai_processing_lambda()
        self.voice_processing_lambda = self._create_voice_processing_lambda()

        # Create API Gateway
        self.api_gateway = self._create_api_gateway()

        # Create SNS topics
        self.notification_topic = sns.Topic(
            self,
            "NotificationTopic",
            topic_name="genai-cs-notifications",
            master_key=self.kms_key,
        )

        # Create SQS queues
        self.processing_queue = sqs.Queue(
            self,
            "ProcessingQueue",
            queue_name="genai-cs-processing",
            encryption=sqs.QueueEncryption.KMS,
            encryption_master_key=self.kms_key,
            visibility_timeout=Duration.minutes(5),
        )

        # Create CloudWatch dashboard
        self._create_cloudwatch_dashboard()

        # Output important values
        CfnOutput(
            self,
            "ApiGatewayUrl",
            value=self.api_gateway.url,
            description="API Gateway URL",
        )

        CfnOutput(
            self,
            "S3BucketName",
            value=self.s3_bucket.bucket_name,
            description="S3 Bucket Name",
        )

        CfnOutput(
            self,
            "OpenSearchEndpoint",
            value=self.opensearch_domain.domain_endpoint,
            description="OpenSearch Domain Endpoint",
        )

    def _create_redis_security_group(self) -> ec2.SecurityGroup:
        """Create security group for Redis cluster"""
        sg = ec2.SecurityGroup(
            self,
            "RedisSecurityGroup",
            vpc=self.vpc,
            description="Security group for Redis cluster",
        )

        # Allow access from Lambda functions
        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(6379),
            description="Allow Redis access from VPC",
        )

        return sg

    def _create_opensearch_security_group(self) -> ec2.SecurityGroup:
        """Create security group for OpenSearch domain"""
        sg = ec2.SecurityGroup(
            self,
            "OpenSearchSecurityGroup",
            vpc=self.vpc,
            description="Security group for OpenSearch domain",
        )

        # Allow access from Lambda functions
        sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS access from VPC",
        )

        return sg

    def _create_api_lambda(self) -> _lambda.Function:
        """Create API Lambda function"""
        return _lambda.Function(
            self,
            "ApiLambda",
            function_name="genai-cs-api",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="main.handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.minutes(5),
            memory_size=1024,
            environment={
                "MONGODB_URL": "mongodb://localhost:27017",  # Will be replaced with actual MongoDB
                "REDIS_URL": f"redis://{self.redis_cluster.attr_redis_endpoint_address}:6379",
                "S3_BUCKET": self.s3_bucket.bucket_name,
                "OPENSEARCH_ENDPOINT": self.opensearch_domain.domain_endpoint,
                "DYNAMODB_TABLE_PREFIX": "genai-cs",
            },
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[self._create_lambda_security_group()],
            log_retention=logs.RetentionDays.ONE_MONTH,
        )

    def _create_ai_processing_lambda(self) -> _lambda.Function:
        """Create AI processing Lambda function"""
        return _lambda.Function(
            self,
            "AiProcessingLambda",
            function_name="genai-cs-ai-processing",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="ai_processor.handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.minutes(15),
            memory_size=2048,
            environment={
                "BEDROCK_MODEL_ID": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "BEDROCK_REGION": self.region,
            },
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[self._create_lambda_security_group()],
            log_retention=logs.RetentionDays.ONE_MONTH,
        )

    def _create_voice_processing_lambda(self) -> _lambda.Function:
        """Create voice processing Lambda function"""
        return _lambda.Function(
            self,
            "VoiceProcessingLambda",
            function_name="genai-cs-voice-processing",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="voice_processor.handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.minutes(10),
            memory_size=1536,
            environment={
                "TRANSCRIBE_LANGUAGE": "en-US",
                "POLLY_VOICE_ID": "Joanna",
                "S3_BUCKET": self.s3_bucket.bucket_name,
            },
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[self._create_lambda_security_group()],
            log_retention=logs.RetentionDays.ONE_MONTH,
        )

    def _create_lambda_security_group(self) -> ec2.SecurityGroup:
        """Create security group for Lambda functions"""
        sg = ec2.SecurityGroup(
            self,
            "LambdaSecurityGroup",
            vpc=self.vpc,
            description="Security group for Lambda functions",
        )

        # Allow outbound HTTPS traffic
        sg.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS outbound",
        )

        # Allow outbound HTTP traffic
        sg.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP outbound",
        )

        return sg

    def _create_api_gateway(self) -> apigateway.RestApi:
        """Create API Gateway"""
        api = apigateway.RestApi(
            self,
            "GenaiCustomerServiceApi",
            rest_api_name="GenAI Customer Service API",
            description="API for GenAI Customer Service",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["*"],
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                allow_headers=["Content-Type", "Authorization"],
            ),
        )

        # Add API Gateway integration with Lambda
        api_lambda_integration = apigateway.LambdaIntegration(
            self.api_lambda,
            request_templates={"application/json": '{"statusCode": "200"}'},
        )

        # Add resources and methods
        api.root.add_method("ANY", api_lambda_integration)
        
        # Add proxy resource for all paths
        proxy = api.root.add_resource("{proxy+}")
        proxy.add_method("ANY", api_lambda_integration)

        return api

    def _create_cloudwatch_dashboard(self) -> cloudwatch.Dashboard:
        """Create CloudWatch dashboard"""
        dashboard = cloudwatch.Dashboard(
            self,
            "GenaiCustomerServiceDashboard",
            dashboard_name="GenAI-Customer-Service",
        )

        # Add widgets for key metrics
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="API Requests",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/ApiGateway",
                        metric_name="Count",
                        dimensions_map={"ApiName": self.api_gateway.rest_api_name},
                    )
                ],
            ),
            cloudwatch.GraphWidget(
                title="Lambda Errors",
                left=[
                    cloudwatch.Metric(
                        namespace="AWS/Lambda",
                        metric_name="Errors",
                        dimensions_map={"FunctionName": self.api_lambda.function_name},
                    )
                ],
            ),
        )

        return dashboard
