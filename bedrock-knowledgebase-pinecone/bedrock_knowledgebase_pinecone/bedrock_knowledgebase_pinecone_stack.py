from aws_cdk import (
    # Duration,
    Stack,
    aws_bedrock as bedrock,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct


class BedrockKnowledgebasePineconeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.bucket = s3.Bucket(
            self,
            "KnowledgeBaseDocuments",
        )

        api_secret_arn = kwargs.get(api_secret_arn)
        connection_string = kwargs.get(connection_string)
        embedding_model_arn = (
            "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
        )

        bedrock_access = iam.PolicyStatement(
            actions=["bedrock:*"],
            resources=["arn:aws:bedrock:us-east-1::foundation-model/*"],
        )
        s3_list_access = iam.PolicyStatement(
            actions=["s3:ListBucket"], resources=[self.bucket.bucket_arn]
        )
        s3_object_access = iam.PolicyStatement(
            actions=["s3:GetObject"], resources=[self.bucket.bucket_arn + "/*"]
        )
        secretsmanager_access = iam.PolicyStatement(
            actions=["secretsmanager:GetSecretValue"], resources=[api_secret_arn]
        )

        knowledge_base_service_role = iam.Role(assumed_by="bedrock.amazonaws.com")
        knowledge_base_service_role.add_to_policy(bedrock_access)
        knowledge_base_service_role.add_to_policy(s3_list_access)
        knowledge_base_service_role.add_to_policy(s3_object_access)
        knowledge_base_service_role.add_to_policy(secretsmanager_access)

        cfn_knowledge_base = bedrock.CfnKnowledgeBase(
            self,
            "MyCfnKnowledgeBase",
            knowledge_base_configuration=bedrock.CfnKnowledgeBase.KnowledgeBaseConfigurationProperty(
                type="VECTOR",
                vector_knowledge_base_configuration=bedrock.CfnKnowledgeBase.VectorKnowledgeBaseConfigurationProperty(
                    embedding_model_arn=embedding_model_arn
                ),
            ),
            name="name",
            role_arn=knowledge_base_service_role.role_arn,
            storage_configuration=bedrock.CfnKnowledgeBase.StorageConfigurationProperty(
                type="VECTOR",
                pinecone_configuration=bedrock.CfnKnowledgeBase.PineconeConfigurationProperty(
                    connection_string=connection_string,
                    credentials_secret_arn=api_secret_arn,
                    field_mapping=bedrock.CfnKnowledgeBase.PineconeFieldMappingProperty(
                        metadata_field="metadataField", text_field="textField"
                    ),
                ),
            ),
        )

        cfn_data_source = bedrock.CfnDataSource(
            self,
            "MyCfnDataSource",
            data_source_configuration=bedrock.CfnDataSource.DataSourceConfigurationProperty(
                s3_configuration=bedrock.CfnDataSource.S3DataSourceConfigurationProperty(
                    bucket_arn=self.bucket.bucket_arn,
                ),
                type="S3",
            ),
            knowledge_base_id=cfn_knowledge_base.attr_knowledge_base_id,
            name="name",
            # the properties below are optional
        )
