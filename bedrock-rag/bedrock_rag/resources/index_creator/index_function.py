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
    index_name = "vector-index"
    index_body = {"settings": {"index": {"number_of_shards": 4}}}
    client.indices.create

    return {"PhysicalResourceId": physical_id}


def on_update(event):
    physical_id = event["PhysicalResourceId"]
    props = event["ResourceProperties"]
    print("update resource %s with props %s" % (physical_id, props))
    # ...


def on_delete(event):
    physical_id = event["PhysicalResourceId"]
    print("delete resource %s" % physical_id)
    # ...
