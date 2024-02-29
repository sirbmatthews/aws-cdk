#!/usr/bin/env python3
import os

import aws_cdk as cdk

from sqs_trigger_lambda.sqs_trigger_lambda_stack import SqsTriggerLambdaStack


app = cdk.App()
SqsTriggerLambdaStack(app, "SqsTriggerLambdaStack", env = cdk.Environment(account = os.getenv('CDK_DEFAULT_ACCOUNT'), region = os.getenv('CDK_DEFAULT_REGION')))

app.synth()
