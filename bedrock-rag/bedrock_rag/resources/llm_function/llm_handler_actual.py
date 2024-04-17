import boto3
import json

import os
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth


session = boto3.Session()
bedrock = session.client(
    "bedrock-runtime",
    "eu-central-1",
)


# instantiating the OpenSearch client, and passing in the CLI profile
opensearch = session.client("opensearchserverless")
host = os.getenv("opensearch_endpoint")
region = "eu-central-1"
service = "aoss"
credentials = session.get_credentials()
auth = AWSV4SignerAuth(credentials, region, service)

client = OpenSearch(
    hosts=[{"host": host, "port": 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20,
)


def llm_handler(event, context):
    user_input = event.get("body")
    if user_input is None:
        return {"statusCode": 400, "body": "No body found in the event"}
    try:
        answer = answer_query(user_input=user_input)
        return {"statusCode": 200, "body": answer}
    except:
        return {"statusCode": 400, "body": "Not able to process user input"}


def get_embedding(body):
    """
    This function is used to generate the embeddings for each question the user submits.
    :param body: This is the question that is passed in to generate an embedding
    :return: A vector containing the embeddings of the passed in content
    """
    # defining the embeddings model
    modelId = "amazon.titan-embed-text-v1"
    accept = "application/json"
    contentType = "application/json"
    # invoking the embedding model
    response = bedrock.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    # reading in the specific embedding
    response_body = json.loads(response.get("body").read())
    embedding = response_body.get("embedding")
    return embedding


def answer_query(user_input):
    """
    This function takes the user question, creates an embedding of that question,
    and performs a KNN search on your Amazon OpenSearch Index. Using the most similar results it feeds that into the Prompt
    and LLM as context to generate an answer.
    :param user_input: This is the natural language question that is passed in through the app.py file.
    :return: The answer to your question from the LLM based on the context that was provided by the KNN search of OpenSearch.
    """
    # Setting primary variables, of the user input
    userQuery = user_input
    # formatting the user input
    userQueryBody = json.dumps({"inputText": userQuery})
    # creating an embedding of the user input to perform a KNN search with
    userVectors = get_embedding(userQueryBody)
    # the query parameters for the KNN search performed by Amazon OpenSearch with the generated User Vector passed in.
    # TODO: If you wanted to add pre-filtering on the query you could by editing this query!
    query = {
        "size": 3,
        "query": {"knn": {"vectors": {"vector": userVectors, "k": 3}}},
        "_source": True,
        "fields": ["text"],
    }
    # performing the search on OpenSearch passing in the query parameters constructed above
    response = client.search(body=query, index=os.getenv("vector_index_name"))

    # Format Json responses into text
    similaritysearchResponse = ""
    # iterating through all the findings of Amazon openSearch and adding them to a single string to pass in as context
    for i in response["hits"]["hits"]:
        outputtext = i["fields"]["text"]
        similaritysearchResponse = (
            similaritysearchResponse + "Info = " + str(outputtext)
        )

        similaritysearchResponse = similaritysearchResponse
    # Configuring the Prompt for the LLM
    # TODO: EDIT THIS PROMPT TO OPTIMIZE FOR YOUR USE CASE
    prompt_data = f"""\n\nHuman: You are an AI assistant that will help people answer questions they have. Answer the provided question to the best of your ability using the information provided in the Context. 
    Summarize the answer and provide sources to where the relevant information can be found. 
    Include this at the end of the response.
    Provide information based on the context provided.
    Format the output in human readable format - use paragraphs and bullet lists when applicable
    Answer in detail with no preamble
    If you are unable to answer accurately, please say so.
    Please mention the sources of where the answers came from by referring to page numbers, specific books and chapters!

    Question: {userQuery}

    Here is the text you should use as context: {similaritysearchResponse}

    \n\nAssistant:

    """
    # Configuring the model parameters, preparing for inference
    # TODO: TUNE THESE PARAMETERS TO OPTIMIZE FOR YOUR USE CASE
    prompt = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "temperature": 0.5,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": prompt_data}]}
        ],
    }
    # formatting the prompt as a json string
    json_prompt = json.dumps(prompt)
    # invoking Claude3, passing in our prompt
    response = bedrock.invoke_model(
        body=json_prompt,
        modelId="anthropic.claude-v2:1",
        accept="application/json",
        contentType="application/json",
    )
    # getting the response from Claude3 and parsing it to return to the end user
    response_body = json.loads(response.get("body").read())
    # the final string returned to the end user
    answer = response_body["content"][0]["text"]
    # returning the final string to the end user
    return answer
