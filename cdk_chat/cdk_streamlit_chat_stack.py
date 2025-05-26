from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam,
    aws_logs as logs,
    CfnOutput,
    RemovalPolicy,
)
from constructs import Construct

class CdkStreamlitChatStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, properties, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Get the ECR repository from properties
        ecr_repository = properties.get("ECR_REPO")
        if not ecr_repository:
            raise ValueError("ECR repository not found in properties")

        # Create a VPC
        vpc = ec2.Vpc(self, "StreamlitVpc",
            max_azs=2,
            nat_gateways=1,
        )

        # Create an ECS cluster
        cluster = ecs.Cluster(self, "StreamlitCluster",
            vpc=vpc,
            container_insights=True,
        )

        # Create a task execution role
        execution_role = iam.Role(self, "StreamlitTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess")
            ]
        )

        # Create a task role with permissions to access AWS Bedrock
        task_role = iam.Role(self, "StreamlitTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        
        # Add Bedrock permissions to the task role
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess")
        )

        # Create a log group for the container
        log_group = logs.LogGroup(self, "StreamlitLogGroup",
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_WEEK
        )

        # Create a Fargate service using the Application Load Balanced Fargate Service pattern
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(self, "StreamlitService",
            cluster=cluster,
            memory_limit_mib=2048,
            cpu=512,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(ecr_repository),
                container_port=8501,  # Streamlit default port
                log_driver=ecs.LogDrivers.aws_logs(
                    stream_prefix="streamlit",
                    log_group=log_group
                ),
                task_role=task_role,
                execution_role=execution_role,
                environment={
                    "AWS_DEFAULT_REGION": self.region
                }
            ),
            public_load_balancer=True,
            assign_public_ip=True,
        )

        # Configure health check for the target group
        fargate_service.target_group.configure_health_check(
            path="/",
            healthy_http_codes="200,302",  # Streamlit may redirect, so include 302
            interval=Duration.seconds(60),
            timeout=Duration.seconds(30),
        )

        # Auto-scaling configuration
        scaling = fargate_service.service.auto_scale_task_count(
            max_capacity=5,
            min_capacity=1,
        )
        
        scaling.scale_on_cpu_utilization("CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )

        # Output the load balancer URL
        CfnOutput(self, "StreamlitAppURL",
            value=f"http://{fargate_service.load_balancer.load_balancer_dns_name}",
            description="URL of the Streamlit application"
        )
