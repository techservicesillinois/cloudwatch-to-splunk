## Running lambda in Docker as a "server" in a terminal window

```
# Set registry ID into environment variable.
typeset -x ECR_REGISTRY=974092523866.dkr.ecr.us-east-2.amazonaws.com;

# Get ECR login token, and log in to ECR registry.
aws ecr get-login-password --region us-east-2 | \
    docker login --username AWS --password-stdin ${ECR_REGISTRY};
    
# Run lambda function in Docker container.
docker run --platform linux/amd64 -p 9000:8080 lambda-function;
```

## Local testing of local Docker deployment of lambda "client"

One can test the lambda function in a local Docker container before deploying it
to AWS.

First, deploy the lambda function locally in Docker using the process
described above. The lambda function is accessed via HTTP `POST` requests
to a server on port 9000.
In order to do this, the `POST` data expected by the lambda function needs to be
emulated and then sent (via standard input) to the `http` command-line utility.

The scripts emulate what happens when lambda function is triggered by a
CloudWatch event when the lambda function is subscribed to by a CloudWatch
log group.

If necessary, refer to the webpage [Deploy Python Lambda functions with
container images](https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-instructions). In place of `curl`, this document uses the `httpie`
package, which is available on PyPI.

```sh
# Change to the `test` directory, which contains the scripts to generate and format
# a CloudWatch log payload, injecting them via an HTTP `POST` to the lambda function.
cd test;

# Generate JSON representing randomized CloudWatch messages, convert them into
# the payload format that CloudWatch passes to the lambda function to which the
# log stream is subscribed.

./make_random_cloudwatch_json --service roma-example | \
./build_cloudwatch_payload | \
	http POST http://localhost:9000/2015-03-31/functions/function/invocations
```

Look at the terminal window where the lambda was launched locally; the output
produced by the function will indicate any problems.