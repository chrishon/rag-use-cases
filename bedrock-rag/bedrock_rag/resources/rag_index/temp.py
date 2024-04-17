import sys
import time
from opensearchpy.client import OpenSearch
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from typing import List, Tuple
import logging
import numpy as np
import boto3

from langchain.llms.bedrock import Bedrock
from langchain.embeddings.bedrock import BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain.vectorstores import OpenSearchVectorSearch

logger = logging.getLogger()
logging.basicConfig(
    format="%(asctime)s,%(module)s,%(processName)s,%(levelname)s,%(message)s",
    level=logging.INFO,
    stream=sys.stderr,
)


"""
1. Connecting OpenSearch in AWS done in multiple ways. here we are going to use userid and password to connect. 
2. Opensearch cluster can be inside VPC or Public. Recommended in inside VPC for all good reasons. Here for this demo I have mdae public.
3. Opensearch is massively sclabale search engine , I have used it mostly for UI applications to render data in fraction of second. 
   However it can also be used for Vector store.
4. It provides simlarity search using KNN, Cosine or more. We will have separate document for that.
5. Here we will read PDF file and store in Openserach so that we can use that in our RAG Architecture.

"""


# Here Keeping the required parameter. can be used from config store.
http_auth = ("ll_vector", "@")
opensearch_domain_endpoint = (
    "https://search-llm-vectordb-1-shpuq.us-east-1.es.amazonaws.com"
)
aws_region = "us-east-1"
index_name = "llm_vector_index2"

max_os_doc = 500
chunk_size_per_doc = 600
chunk_overlap_per_doc = 20


from botocore.config import Config

retry_config = Config(
    region_name="us-east-1", retries={"max_attempts": 10, "mode": "standard"}
)

# Creating boto3 session by passing profile information. Profile can be parametrized depeding upon the env you are using
session = boto3.session.Session(profile_name="bdl-ml-beta")
"""" 
btot3 provides two different client to ivoke bedrock operation.
1. bedrock : creating and managing Bedrock models.
2. bedrock-runtime : Running inference using Bedrock models.
"""
boto3_bedrock = session.client("bedrock", config=retry_config)
boto3_bedrock_runtime = session.client("bedrock-runtime", config=retry_config)
EMBEDDINGS_MODEL_ID = "amazon.titan-embed-text-v1"
brrkEmbeddings = BedrockEmbeddings(
    model_id=EMBEDDINGS_MODEL_ID,
    client=boto3_bedrock_runtime,
)
bedrock_llm = Bedrock(
    model_id="anthropic.claude-v1",
    client=boto3_bedrock_runtime,
    model_kwargs={"max_tokens_to_sample": 200},
)


def create_chunks(directory_path):
    print(f"Loading directory {directory_path}")
    loader = PyPDFDirectoryLoader(directory_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=1000,
        chunk_overlap=100,
    )
    docs = text_splitter.split_documents(documents)
    avg_doc_length = lambda documents: sum(
        [len(doc.page_content) for doc in documents]
    ) // len(documents)
    avg_char_count_pre = avg_doc_length(documents)
    avg_char_count_post = avg_doc_length(docs)
    print(
        f"Average length among {len(documents)} documents loaded is {avg_char_count_pre} characters."
    )
    print(
        f"After the split we have {len(docs)} documents more than the original {len(documents)}."
    )
    print(
        f"Average length among {len(docs)} documents (after split) is {avg_char_count_post} characters."
    )
    sample_embedding = np.array(brrkEmbeddings.embed_query(docs[0].page_content))
    print("Sample embedding of a document chunk: ", sample_embedding)
    print("Size of the embedding: ", sample_embedding.shape)

    # split docs into chunks.
    st = time.time()

    # add a custom metadata field, such as timestamp
    logger.info(f"Docs length is: {len(docs)}")
    for doc in docs:
        doc.metadata["timestamp"] = time.time()
        doc.metadata["embeddings_model"] = EMBEDDINGS_MODEL_ID

    chunks = text_splitter.create_documents(
        [doc.page_content for doc in docs], metadatas=[doc.metadata for doc in docs]
    )
    et = time.time() - st
    logger.info(f"Time taken: {et} seconds. {len(chunks)} chunks generated")
    return chunks


def check_if_index_exists(
    index_name: str, region: str, host: str, http_auth: Tuple[str, str]
) -> OpenSearch:
    aos_client = OpenSearch(
        hosts=[{"host": host.replace("https://", ""), "port": 443}],
        http_auth=http_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )
    exists = aos_client.indices.exists(index_name)
    print("exist check", exists)
    return exists


if __name__ == "__main__":

    index_exists = check_if_index_exists(
        index_name, aws_region, opensearch_domain_endpoint, http_auth
    )
    if not index_exists:
        logger.info(f"index :{index_name} is not existing ")

    data_path = "/Users/ss/projects/dev/learning/spark"
    logger.info(f"Passing the pathe where document is stored : {data_path} ")
    chunks = create_chunks(data_path)
    docsearch = OpenSearchVectorSearch.from_documents(
        index_name=index_name,
        documents=chunks,
        embedding=brrkEmbeddings,
        opensearch_url=opensearch_domain_endpoint,
        http_auth=http_auth,
    )

    index_exists = check_if_index_exists(
        index_name, aws_region, opensearch_domain_endpoint, http_auth
    )

    if index_exists:
        logger.info(f"index got created is :{index_name}  ")
