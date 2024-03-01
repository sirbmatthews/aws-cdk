#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { SqsTriggerLambdaStack } from '../lib/sqs_trigger_lambda-stack';

const app = new cdk.App();
new SqsTriggerLambdaStack(app, 'SqsTriggerLambdaStack', { env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION} });