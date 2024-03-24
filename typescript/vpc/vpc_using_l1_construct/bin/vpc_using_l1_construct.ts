#!/usr/bin/env node

import * as cdk from 'aws-cdk-lib';
import { VpcStack } from '../lib/vpc_using_l1_construct-stack';

const app = new cdk.App();
new VpcStack(app, 'VpcStack');