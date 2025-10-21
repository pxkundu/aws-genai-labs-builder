from aws_cdk import (
    Stack,
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ecr as ecr,
    aws_elasticloadbalancingv2 as elbv2,
    CfnOutput,
    Duration,
    Tags
)
from constructs import Construct

class GenAIMinimalStarterStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC for EKS cluster
        vpc = ec2.Vpc(
            self, "GenAIVPC",
            max_azs=2,
            nat_gateways=1,
            enable_dns_hostnames=True,
            enable_dns_support=True
        )

        # EKS Cluster
        cluster = eks.Cluster(
            self, "GenAICluster",
            version=eks.KubernetesVersion.V1_28,
            vpc=vpc,
            default_capacity=0,  # We'll add managed node groups
            cluster_logging=[
                eks.ClusterLoggingTypes.API,
                eks.ClusterLoggingTypes.AUDIT,
                eks.ClusterLoggingTypes.AUTHENTICATOR,
                eks.ClusterLoggingTypes.CONTROLLER_MANAGER,
                eks.ClusterLoggingTypes.SCHEDULER
            ]
        )

        # Managed Node Group
        node_group = cluster.add_nodegroup_capacity(
            "GenAINodeGroup",
            instance_types=[ec2.InstanceType("t3.medium")],
            min_size=1,
            max_size=3,
            desired_size=2,
            disk_size=20,
            ami_type=eks.NodegroupAmiType.AL2_X86_64,
            capacity_type=eks.CapacityType.ON_DEMAND
        )

        # ECR Repository for container images
        ecr_repo = ecr.Repository(
            self, "GenAIContainerRepo",
            repository_name="genai-minimal-starter",
            image_scan_on_push=True,
            lifecycle_rules=[
                ecr.LifecycleRule(
                    max_image_count=10,
                    rule_priority=1
                )
            ]
        )

        # OIDC Provider for IRSA (IAM Roles for Service Accounts)
        oidc_provider = eks.OpenIdConnectProvider(
            self, "GenAIOIDCProvider",
            url=cluster.cluster_open_id_connect_issuer_url,
            thumbprints=["9e99a48a9960b14926bb7f3b02e22da2b0ab7280"]
        )

        # Service Account for ALB Controller
        alb_service_account = cluster.add_service_account(
            "ALBServiceAccount",
            name="aws-load-balancer-controller",
            namespace="kube-system"
        )

        # ALB Controller IAM Policy
        alb_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "iam:CreateServiceLinkedRole",
                "ec2:DescribeAccountAttributes",
                "ec2:DescribeAddresses",
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeInternetGateways",
                "ec2:DescribeVpcs",
                "ec2:DescribeVpcPeeringConnections",
                "ec2:DescribeSubnets",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeInstances",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribeTags",
                "ec2:GetCoipPoolUsage",
                "ec2:DescribeCoipPools",
                "elasticloadbalancing:DescribeLoadBalancers",
                "elasticloadbalancing:DescribeLoadBalancerAttributes",
                "elasticloadbalancing:DescribeListeners",
                "elasticloadbalancing:DescribeListenerCertificates",
                "elasticloadbalancing:DescribeSSLPolicies",
                "elasticloadbalancing:DescribeRules",
                "elasticloadbalancing:DescribeTargetGroups",
                "elasticloadbalancing:DescribeTargetGroupAttributes",
                "elasticloadbalancing:DescribeTargetHealth",
                "elasticloadbalancing:DescribeTags"
            ],
            resources=["*"]
        )

        alb_service_account.add_to_policy(alb_policy)

        # Outputs
        CfnOutput(
            self, "ClusterName",
            value=cluster.cluster_name,
            description="EKS Cluster Name"
        )

        CfnOutput(
            self, "ClusterEndpoint",
            value=cluster.cluster_endpoint,
            description="EKS Cluster Endpoint"
        )

        CfnOutput(
            self, "ECRRepositoryURI",
            value=ecr_repo.repository_uri,
            description="ECR Repository URI"
        )

        CfnOutput(
            self, "VPCId",
            value=vpc.vpc_id,
            description="VPC ID"
        )

        # Tag resources
        Tags.of(self).add("Project", "GenAI-Minimal-Starter")
        Tags.of(self).add("Environment", "dev")
