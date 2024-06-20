FROM public.ecr.aws/lambda/python:3.12

# ENV TZ='America/Chicago'

# Copy requirements.txt.
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install prerequisite packages.
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

RUN pip list

# Copy lambda function.
COPY lambda.py ${LAMBDA_TASK_ROOT}

# Set CMD to the lambda handler (could also be done as a parameter
# override outside of the Dockerfile).
CMD [ "lambda.handler" ]
