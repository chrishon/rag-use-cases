from aws_cdk import (
    # Duration,
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_s3_notifications as notifications,
    Duration,
    Fn,
    # aws_sqs as sqs,
)
from constructs import Construct


class KnowledgeBaseStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        opensearch_endpoint = Fn.import_value("VectorDB-OpenSearchEndpoint")
        collection_name = Fn.import_value("VectorDB-OpenSearch-CollectionName")

        function = _lambda.Function(
            self,
            "lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="ragindex.indexer",
            code=_lambda.Code.from_asset(
                "bedrock_rag/resources/rag_index/rag_index_zipped.zip"
            ),
            memory_size=256,
            timeout=Duration.seconds(60 * 5),
            environment={"opensearch_endpoint": opensearch_endpoint},
        )

        bedrock_access = iam.PolicyStatement(
            actions=["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
            resources=["arn:aws:bedrock:*::foundation-model/*"],
        )

        opensearch_collection_access = iam.PolicyDocument(
            actions=[
                "aoss:CreateCollectionItems",
                "aoss:DeleteCollectionItems",
                "aoss:UpdateCollectionItems",
                "aoss:DescribeCollectionItems",
            ],
            resource=f"collection/{collection_name}",
        )
        opensearch_data_access = iam.PolicyDocument(
            actions=[
                "aoss:CreateIndex",
                "aoss:DeleteIndex",
                "aoss:UpdateIndex",
                "aoss:DescribeIndex",
                "aoss:ReadDocument",
                "aoss:WriteDocument",
            ],
            resource=f"index/{collection_name}/*",
        )

        function.add_to_role_policy(opensearch_collection_access)
        function.add_to_role_policy(opensearch_data_access)

        bucket = s3.Bucket(
            self,
            "KnowledgeBaseDocuments",
        )

        bucket.grant_read_write(function)
        notification = notifications.LambdaDestination(function)

        # assign notification for the s3 event type (ex: OBJECT_CREATED)
        s3.add_event_notification(s3.EventType.OBJECT_CREATED, notification)
