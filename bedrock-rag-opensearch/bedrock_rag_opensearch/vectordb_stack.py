from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_opensearchservice as opensearch,
    Duration,
    # aws_sqs as sqs,
)
from constructs import Construct


class VectorDBStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc_id: str,
        private_subnet_ids: list,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        domain = opensearch.Domain(
            self,
            "RAG-OSDomain",
            version=opensearch.EngineVersion.OPENSEARCH_2_11,
            node_to_node_encryption=True,
            encryption_at_rest=opensearch.EncryptionAtRestOptions(
                enabled=True,
            ),
            vpc=vpc_id,  ##?ref auf arn??
            vpc_subnets=private_subnet_ids,
        )
