#!  /usr/bin/env zsh

ECR_BASE="974092523866.dkr.ecr.us-east-2.amazonaws.com"
ECR_IMAGE="cloudwatch-to-splunk:develop"

ecr_path=${ECR_BASE}/${ECR_IMAGE};

aws lambda create-function \
  --function-name cloudwatch-to-splunk-new \
  --package-type Image \
  --code ImageUri=${ecr_path} \
  --role arn:aws:iam::452834793638:role/cloudwatch-to-splunk-new
