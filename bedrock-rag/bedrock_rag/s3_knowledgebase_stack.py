from aws_cdk import (
    # Duration,
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_s3_notifications as notifications,
    Duration,
    # aws_sqs as sqs,
)
from constructs import Construct


class KnowledgeBaseStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        ######################################
        ######## S3 Bucket

        function = _lambda.Function(
            self,
            "lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="ragindex.send_to_opensearch",  # Assuming index.py with a function named handler
            code=_lambda.Code.from_asset("bedrock_rag/resources/rag_index"),
            memory_size=256,
            timeout=Duration.seconds(60 * 5),
        )

        bucket = s3.Bucket(
            self,
            "KnowledgeBaseDocuments",
            bucket_name="rag-knowledge-base",  # specify a unique bucket name
        )

        notification = notifications.LambdaDestination(function)

        # assign notification for the s3 event type (ex: OBJECT_CREATED)
        s3.add_event_notification(s3.EventType.OBJECT_CREATED, notification)
