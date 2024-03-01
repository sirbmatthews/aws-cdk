# TypeScript Projects

![Language-Support: Stable](https://img.shields.io/badge/language--support-stable-success.svg?style=for-the-badge)

This section contains all the CDK projects written in TypeScript.

## Running Projects

### To run a Typescript project, execute the following:

```sh
$ npm install -g aws-cdk
$ cd typescript/PROJECT_DIRECTORY
$ npm install
$ cdk deploy
```

Then, to dispose of the stack/s afterwards

```
$ cdk destroy
```

### To dispose of the stack afterwards:

```
$ cdk destroy
```

## Table of Contents

| Project | Description |
|---------|-------------|
| [jenkins_server](https://github.com/sirbmatthews/aws-cdk/tree/main/typescript/jenkins_server) | Shows the creation of an EC2 instance with a Jenkins Server in an existing Default VPC |
| [vpc](https://github.com/sirbmatthews/aws-cdk/tree/main/typescript/vpc) | Shows the creation of a VPC using L1 & L3 constructs |
| [sqs_trigger_lambda](https://github.com/sirbmatthews/aws-cdk/tree/main/typescript/sqs_trigger_lambda) | Shows how to trigger a Lambda function using SQS. |