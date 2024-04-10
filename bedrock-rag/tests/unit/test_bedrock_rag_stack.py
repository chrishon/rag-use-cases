import aws_cdk as core
import aws_cdk.assertions as assertions

from bedrock_rag.bedrock_rag_stack import BedrockRagStack

# example tests. To run these tests, uncomment this file along with the example
# resource in bedrock_rag/bedrock_rag_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = BedrockRagStack(app, "bedrock-rag")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })