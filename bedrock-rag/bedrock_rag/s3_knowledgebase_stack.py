from aws_cdk import (
    # Duration,
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    Duration,
    # aws_sqs as sqs,
)
from constructs import Construct


class S3Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        ######################################
        ######## S3 Bucket

        bucket = s3.Bucket(
            self,
            "KnowledgeBaseDocuments",
            bucket_name="rag-knowledge-base",  # specify a unique bucket name
        )
