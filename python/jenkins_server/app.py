#!/usr/bin/env python3
import os

import aws_cdk as cdk

from jenkins_server.jenkins_server_stack import JenkinsServerStack


app = cdk.App()
JenkinsServerStack(app, "JenkinsServerStack", env = cdk.Environment(account = os.getenv('CDK_DEFAULT_ACCOUNT'), region = os.getenv('CDK_DEFAULT_REGION')))

app.synth()
