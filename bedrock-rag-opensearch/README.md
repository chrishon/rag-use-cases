
# RAG with Bedrock and Opensearch (and Textract)

This directory contains the necessary components to deploy a RAG demo on AWS, which uses OpenSearch Serverless and Bedrock to perform RAG based Q&A.

## Beware! 
The running cost of this demo is about 900 USD prt month, don't forget to `cdk destroy --all` after running the demo!


## Prerequisites

The only prerequisites needed to deploy this is an AWS Account with a profile and a Python environment:

First install the CDK CLI:

```
$ npm install -g aws-cdk
```

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

## Deployment

Interacting with the stacks is not necessary unless customization is needed. To deploy the demo take the following steps:

Navigate to the `config/` folder:

```
$ cd config
```

In `constants.py`, write down the specific information on the deployment AWS Account

Following that, make the deploy.sh script executable:

```
$ chmod +x deploy.sh
```

Now run the deployment script, it will ask you for your AWS profile name as well as the option to use Amazon Textract parsing (this is especially useful if the documents contain a lot of tables, as the OCR helps to properly index those in combination with Langchain)

```
$ bash deploy.sh
```

The deployment will also bootstrap your AWS Account, and it may take a while until everything is deployed.

Take note of the API Endpoint in the CLI output, you can use that later with streamlit to test the demo.

After the deployment, a S3 bucket is provided for your documents, upload a PDF and a Lambda function will be triggered which takes care of sending the split documents to OpenSearch.

To test the demo, a streamlit app is provided, first we need to install streamlit:

```
$ pip install streamlit
```

Navigate to the `streamlit/` folder and open `app.py` and replace the endpoint name with your endpoint from the CLI output. After that, you ca run the application:

```
$ streamlit run app.py
```

Now you can test the RAG demo with your own documents.




