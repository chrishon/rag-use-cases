import boto3
import json
from dotenv import load_dotenv
import os
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain_community.document_loaders import S3FileLoader

# loading in environment variables


# instantiating the bedrock client, with specific CLI profile
session = boto3.Session()

bedrock = session.client(
    "bedrock-runtime",
    "eu-central-1",
)
opensearch = session.client("opensearchserverless")
s3 = session.resource("s3")

# Instantiating the OpenSearch client, with specific CLI profile
host = os.getenv("opensearch_endpoint")

region = "eu-central-1"
service = "aoss"
credentials = boto3.Session(profile_name=os.getenv("profile_name")).get_credentials()
auth = AWSV4SignerAuth(credentials, region, service)

client = OpenSearch(
    hosts=[{"host": host, "port": 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20,
)


# Fetch the object from S3


# loading in PDF, can use PyPDFDirectoryLoader if you want to load in a directory of PDFs
# TODO: Change PDF loader and chunker


# implementing a text splitter based on number of characters
# TODO: PLAY WITH THESE VALUES TO OPTIMIZE FOR YOUR USE CASE
text_splitter = RecursiveCharacterTextSplitter(
    # Play with Chunk Size
    chunk_size=600,
    chunk_overlap=100,
)

# Performing the splitting of the document(s)
doc = text_splitter.split_documents(documents)

# Providing insights into the average length of documents, and amount of character before and after splitting
avg_doc_length = lambda documents: sum(
    [len(doc.page_content) for doc in documents]
) // len(documents)
avg_char_count_pre = avg_doc_length(documents)
avg_char_count_post = avg_doc_length(doc)
print(
    f"Average length among {len(documents)} documents loaded is {avg_char_count_pre} characters."
)
print(
    f"After the split we have {len(doc)} documents more than the original {len(documents)}."
)
print(
    f"Average length among {len(doc)} documents (after split) is {avg_char_count_post} characters."
)


def load_document(bucket, key):
    loader = S3FileLoader(bucket, key)
    documents = loader.load()

    return documents


def get_embedding(body):
    """
    This function is used to generate the embeddings for a specific chunk of text
    :param body: This is the example content passed in to generate an embedding
    :return: A vector containing the embeddings of the passed in content
    """
    modelId = "amazon.titan-embed-text-v1"
    accept = "application/json"
    contentType = "application/json"
    response = bedrock.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())
    embedding = response_body.get("embedding")
    return embedding


def indexDoc(client, vectors, text):
    """
    This function indexing the documents and vectors into Amazon OpenSearch Serverless.
    :param client: The instatiation of your OpenSearch Serverless instance.
    :param vectors: The vector you generated with the get_embeddings function that is going to be indexed.
    :param text: The actual text of the document you are storing along with the vector of that text.
    :return: The confirmation that the document was indexed successfully.
    """
    # TODO: You can add more metadata fields if you wanted to!
    indexDocument = {os.getenv("vector_field_name"): vectors, "text": text}
    # Configuring the specific index
    response = client.index(
        index=os.getenv("vector_index_name"), body=indexDocument, refresh=False
    )
    print(response)
    return response


# The process of iterating through each chunk of the document you are trying to index, and generate embeddings for.
for i in doc:
    # The text data of each chunk
    exampleContent = i.page_content
    # Generating the embeddings for each chunk of text data
    exampleInput = json.dumps({"inputText": exampleContent})
    exampleVectors = get_embedding(exampleInput)
    # setting the text data as the text variable, and generated vector to a vector variable
    # TODO: You can add more metadata fields here if you wanted to by configuring it here and adding them to the indexDocument dictionary above
    text = exampleContent
    vectors = exampleVectors
    # calling the indexDoc function, passing in the OpenSearch Client, the created vector, and corresponding text data
    # TODO: If you wanted to add metadata you would pass it in here
    indexDoc(client, vectors, text)
