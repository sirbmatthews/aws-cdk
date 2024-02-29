#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { JenkinsServerStack } from '../lib/jenkins_server-stack';

const app = new cdk.App();
new JenkinsServerStack(app, 'JenkinsServerStack', { env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION }});