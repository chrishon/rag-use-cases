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

import json


class VectorDBServerlessStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc = None,
        subnets: List[ec2.Subnet] = [],
        user_arn=None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env = kwargs.get("env")
        region = env.region
        account = env.account
        collection_name = "vectordb"
        admin_user_arn = user_arn
        encryption_security_policy = json.dumps(
            {
                "Rules": [
                    {
                        "Resource": [f"collection/{collection_name}"],
                        "ResourceType": "collection",
                    }
                ],
                "AWSOwnedKey": True,
            },
            indent=2,
        )

        encryption_security_policy_name = f"{collection_name}-security-policy"
        cfn_encryption_security_policy = aoss.CfnSecurityPolicy(
            self,
            "EncryptionSecurityPolicy",
            policy=encryption_security_policy,
            name=encryption_security_policy_name,
            type="encryption",
        )

        network_security_policy = json.dumps(
            [
                {
                    "Rules": [
                        {
                            "Resource": [f"collection/{collection_name}"],
                            "ResourceType": "dashboard",
                        },
                        {
                            "Resource": [f"collection/{collection_name}"],
                            "ResourceType": "collection",
                        },
                    ],
                    "AllowFromPublic": True,
                }
            ],
            indent=2,
        )

        network_security_policy_name = f"{collection_name}-security-policy"

        cfn_network_security_policy = aoss.CfnSecurityPolicy(
            self,
            "NetworkSecurityPolicy",
            policy=network_security_policy,
            name=network_security_policy_name,
            type="network",
        )

        collection = aoss.CfnCollection(
            self, id="vectordb", name=collection_name, type="VECTORSEARCH"
        )
        collection.add_depends_on(cfn_encryption_security_policy)
        collection.add_dependency(cfn_network_security_policy)

        data_access_policy = json.dumps(
            [
                {
                    "Rules": [
                        {
                            "Resource": [f"collection/{collection_name}"],
                            "Permission": [
                                "aoss:CreateCollectionItems",
                                "aoss:DeleteCollectionItems",
                                "aoss:UpdateCollectionItems",
                                "aoss:DescribeCollectionItems",
                            ],
                            "ResourceType": "collection",
                        },
                        {
                            "Resource": [f"index/{collection_name}/*"],
                            "Permission": [
                                "aoss:CreateIndex",
                                "aoss:DeleteIndex",
                                "aoss:UpdateIndex",
                                "aoss:DescribeIndex",
                                "aoss:ReadDocument",
                                "aoss:WriteDocument",
                            ],
                            "ResourceType": "index",
                        },
                    ],
                    "Principal": [f"{admin_user_arn}"],
                    "Description": "data-access-rule",
                }
            ],
            indent=2,
        )

        data_access_policy_name = f"{collection_name}-policy"

        cfn_access_policy = aoss.CfnAccessPolicy(
            self,
            "OpssDataAccessPolicy",
            name=data_access_policy_name,
            description="Policy for data access",
            policy=data_access_policy,
            type="data",
        )

        CfnOutput(
            self,
            "OpenSearchEndpoint",
            value=collection.attr_collection_endpoint,
            export_name=f"VectorDB-OpenSearchEndpoint",
        )
        CfnOutput(
            self,
            "CollectionName",
            value=collection_name,
            export_name=f"VectorDB-OpenSearch-CollectionName",
        )
        CfnOutput(
            self,
            "DashboardsURL",
            value=collection.attr_dashboard_endpoint,
            export_name=f"{self.stack_name}-DashboardsURL",
        )


# TODO: Create Vector Index in CDK
