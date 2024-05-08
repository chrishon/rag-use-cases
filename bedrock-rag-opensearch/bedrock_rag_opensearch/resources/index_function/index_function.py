import boto3
import json

import os
import time
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth


session = boto3.Session()
bedrock = session.client(
    "bedrock-runtime",
    "eu-central-1",
)


# instantiating the OpenSearch client, and passing in the CLI profile
opensearch = session.client("opensearchserverless")
host = os.getenv("opensearch_endpoint")
index_name = os.getenv("vector_index_name", "vector")
host = host.replace("https://", "")
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
time.sleep(45)


def on_event(event, context):
    print(event)
    request_type = event["RequestType"]
    if request_type == "Create":
        return on_create(event)
    if request_type == "Update":
        return on_update(event)
    if request_type == "Delete":
        return on_delete(event)
    raise Exception("Invalid request type: %s" % request_type)


def on_create(event):
    index_body = {
        "settings": {"index": {"knn": True}},
        "mappings": {
            "properties": {
                "vectors": {
                    "type": "knn_vector",
                    "dimension": 1536,
                    "method": {
                        "engine": "nmslib",
                        "name": "hnsw",
                    },
                }
            }
        },
    }
    client.indices.create(index=index_name, body=index_body)

    return {"statusCode": 200, "body": "Successfully created the vector index"}


def on_update(event):
    pass


def on_delete(event):
    pass
