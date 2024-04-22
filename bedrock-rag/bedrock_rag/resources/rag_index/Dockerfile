FROM public.ecr.aws/lambda/python:3.10

# Copy function code
COPY ragindex.py ${LAMBDA_TASK_ROOT} 
# Install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN python3.10 -m pip install -r requirements.txt --no-cache-dir --disable-pip-version-check
CMD [ "ragindex.indexer" ]
