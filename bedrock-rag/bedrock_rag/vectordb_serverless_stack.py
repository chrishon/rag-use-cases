from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_opensearchserverless as aoss,
    Duration,
    # aws_sqs as sqs,
    Fn,
    aws_ec2 as ec2,
    CfnOutput,
)
from constructs import Construct

from typing import List, Sequence
from .network_stack import NetworkingStack


class VectorDBServerlessStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc = None,
        subnets: List[ec2.Subnet] = [],
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        encryption_policy = aoss.CfnSecurityPolicy(
            self,
            type="encryption",
            id="encryption-policy",
            name="encryption-policy",
            policy='{"Rules":[{"ResourceType":"collection","Resource":["collection/vectordb"]}],"AWSOwnedKey":true}',
        )

        collection = aoss.CfnCollection(
            self, id="vectordb", name="vectordb", type="VECTORSEARCH"
        )
        collection.add_depends_on(encryption_policy)
