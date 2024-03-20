# Python Projects

![Language-Support: Stable](https://img.shields.io/badge/language--support-stable-success.svg?style=for-the-badge)

This section contains all the CDK projects written in Python.

## Running Projects

### To run a project
1. Ensure CDK is installed
```
$ npm install -g aws-cdk
```

2. Create a Python virtual environment
```
$ python3 -m venv .venv
```

3. Activate virtual environment

_On MacOS or Linux_
```
$ source .venv/bin/activate
```

_On Windows_
```
% .venv\Scripts\activate.bat
```

4. Install the required dependencies.

```
$ pip install -r requirements.txt
```

5. Synthesize (`cdk synth`) or deploy (`cdk deploy`) the project

```
$ cdk deploy
```

### To dispose of the stack afterwards:

```
$ cdk destroy
```

## Table of Contents

| Example | Description |
|---------|-------------|
| [hibernating_ec2_instances_in_response_to_cloudwatch_alarm](https://github.com/sirbmatthews/aws-cdk/tree/main/python/hibernating_ec2_instances_in_response_to_cloudwatch_alarm) | Demonstrates the creation of a solution that will find idle instances using an Amazon CloudWatch alarm that monitors the instance’s CPU usage. When the CPU usage consistently drops below the alarm’s threshold, the alarm enters the ALARM state and raises an event used to identify the instance and trigger hibernation.
| [jenkins_server](https://github.com/sirbmatthews/aws-cdk/tree/main/python/jenkins_server) | Shows the creation of an EC2 instance with a Jenkins Server in an existing Default VPC |
| [vpc](https://github.com/sirbmatthews/aws-cdk/tree/main/python/vpc) | Shows the creation of a VPC using L1 & L3 constructs |
| [sqs_trigger_lambda](https://github.com/sirbmatthews/aws-cdk/tree/main/python/sqs_trigger_lambda) | Shows how to trigger a Lambda function using SQS. |