import json
import boto3
import langchain

bedrock = boto3.client("bedrock-runtime")


def indexer(event, context):
    """
    Lambda handler function.

    Parameters:
    event (dict): The event data passed to the Lambda function.
    context (object): The runtime information provided by AWS Lambda.

    Returns:
    dict: A response containing the message.
    """
    query = event.get("body")

    if query is None:
        return {"statusCode": 400, "body": "No body found in the event"}

    # Parse the body as JSON

    # Extract text from the body

    prompt = f"User: {query}\nBot:"
    body = json.dumps(
        {
            "inputText": prompt,
            "textGenerationConfig": {
                "temperature": 0.5,
                "topP": 0.9,
                "maxTokenCount": 300,
            },
        }
    )

    modelId = "amazon.titan-text-express-v1"
    accept = "application/json"
    contentType = "application/json"

    response = bedrock.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )

    # embedding = get_vector_embedding(
    #     question,
    #     bedrock_client,
    #     "amazon.titan-embed-text-v1",  ## TODO adapt modelID for current model
    # )

    response_body = json.loads(response.get("body").read())
    # text
    response_text = response_body["results"][0]["outputText"]
    return {"statusCode": 200, "body": response_text}


def get_vector_embedding(text, bedrock_client, modelId):

    response = bedrock_client.invoke_model(
        body=json.dumps({"inputText": text}),
        modelId=modelId,
        accept="application/json",
        contentType="application/json",
    )

    response_body = json.loads(response.get("body").read())

    return response_body.get("embedding")
