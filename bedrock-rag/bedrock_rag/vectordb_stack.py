# adapted from https://github.com/aws-samples/aws-opensearch-ingestion-tutorials/blob/main/opensearch/cdk_stacks/ops.py

from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_opensearchservice as opensearch,
    Duration,
    # aws_sqs as sqs,
    Fn,
    aws_ec2 as ec2,
)
from constructs import Construct

from typing import List, Sequence
from .network_stack import NetworkingStack


class VectorDBStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc = None,
        subnets: List[ec2.Subnet] = [],
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
            capacity={
                "master_nodes": 3,
                "master_node_instance_type": "r6g.large.search",
                "data_nodes": 3,
                "data_node_instance_type": "r6g.large.search",
            },
            ebs={"volume_size": 10, "volume_type": ec2.EbsDeviceVolumeType.GP3},
            zone_awareness=opensearch.ZoneAwarenessConfig(
                enabled=True, availability_zone_count=3
            ),
            vpc=vpc,
        )
