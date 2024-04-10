from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as lambda_,
    aws_iam as iam,
    Duration
    # aws_sqs as sqs,
)
from constructs import Construct

class BedrockRagStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "BedrockRagQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

        llm_handler = lambda_.Function(
            self, "LLMHandler",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="llm_handler.llm_handler",  # Assuming index.py with a function named handler
            code=lambda_.Code.from_asset("bedrock_rag/resources/llm_function"),
            memory_size=256,
            timeout=Duration.seconds(60*5),
        )

        llm_handler.add_to_role_policy(iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=[
            "bedrock:InvokeModel",
            "bedrock:InvokeModelWithResponseStream"
        ],
        resources=["arn:aws:bedrock:*::foundation-model/*"]

        ######################################
        ######## VPC

        vpc = ec2.Vpc(self, 'rag-vpc', #change to import vpc from other stack
            cidr = '192.168.0.0/24',
            max_azs = 3,
            enable_dns_hostnames = True,
            enable_dns_support = True, 
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name = 'Public-Subnet',
                    subnet_type = ec2.SubnetType.PUBLIC,
                    cidr_mask = 26
                ),
                ec2.SubnetConfiguration(
                    name = 'Private-Subnet',
                    subnet_type = ec2.SubnetType.PRIVATE,
                    cidr_mask = 26
                )
            ],
            nat_gateways = 1,
        )

        ######################################
        ######## S3 Bucket

        bucket = s3.Bucket(self, "KnowledgeBaseDocuments",
            bucket_name="Rag-knowledge-base", # specify a unique bucket name
        )

        ######################################
        ######## OpenSearch

        domain = opensearch.Domain(self, "RAG-OSDomain",
            version=EngineVersion.OPENSEARCH_2_11,
            node_to_node_encryption=True,
            encryption_at_rest=EncryptionAtRestOptions(
                enabled=True,
            )
            vpc=self.vpc, ##?ref auf arn??
            vpc_subnets=[subnet.subnet_id for subnet in self.vpc.private_subnets],
        )

        index_handler = lambda_.Function(
            self, "RAGIndexHandler",
            runtime=lambda_.Runtime.PYTHON_3_10,
            handler="ragindex.indexer",  # Assuming index.py with a function named handler
            code=lambda_.Code.from_asset("bedrock_rag/resources/rag_index"),
            memory_size=256,
            timeout=Duration.seconds(60*5),
        )

        index_handler.add_to_role_policy(iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=[
            "bedrock:InvokeModel",
            "bedrock:InvokeModelWithResponseStream"
            #adapt for s3 & OpenSearch
        ],
        resources=["arn:aws:bedrock:*::foundation-model/*"]
        
    ))
