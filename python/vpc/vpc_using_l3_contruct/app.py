#!/usr/bin/env python3
import os
import aws_cdk as cdk
from vpc.vpc_stack import VpcL3Stack

app = cdk.App()

VpcL3Stack(app, "VpcStack", env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')))
app.synth()
