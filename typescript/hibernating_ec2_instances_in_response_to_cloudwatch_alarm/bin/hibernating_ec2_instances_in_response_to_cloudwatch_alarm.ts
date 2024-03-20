#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { HibernatingEc2InstancesInResponseToCloudwatchAlarmStack } from '../lib/hibernating_ec2_instances_in_response_to_cloudwatch_alarm-stack';
import { HibernatingEc2InstanceStack } from '../lib/hibernating_ec2_instance-stack';

const app = new cdk.App();
new HibernatingEc2InstanceStack(app, 'HibernatingEc2InstanceStack');
new HibernatingEc2InstancesInResponseToCloudwatchAlarmStack(app, 'HibernatingEc2InstancesInResponseToCloudwatchAlarmStack');