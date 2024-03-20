import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { CfnParameter, Duration, Fn, RemovalPolicy, Stack } from 'aws-cdk-lib' 
import { Alarm, ComparisonOperator, Metric } from 'aws-cdk-lib/aws-cloudwatch'
import { EventPattern, Rule } from 'aws-cdk-lib/aws-events'
import { LambdaFunction } from 'aws-cdk-lib/aws-events-targets'
import { Effect, Policy, PolicyStatement, Role, ServicePrincipal } from 'aws-cdk-lib/aws-iam'
import { Architecture, Code, Function, Runtime } from 'aws-cdk-lib/aws-lambda'
import { LogGroup, RetentionDays } from 'aws-cdk-lib/aws-logs'

export class HibernatingEc2InstancesInResponseToCloudwatchAlarmStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const instance_id = new CfnParameter(
      this, 'InstanceId',
      {
        description: 'Instance Id of the EC2 instance to be monitored',
        type: 'String'
      }
  )
  
  const hibernate_policy = new Policy(
      this, 'AllowHibernateEC2InstancePolicy',
      {
        policyName: 'AllowHibernateEC2InstancePolicy',
        statements: [
            new PolicyStatement({
                actions: ['ec2:Stop*'],
                effect: Effect.ALLOW,
                resources: ['*']
            }),
            new PolicyStatement({
                actions: [ 'logs:CreateLogStream', 'logs:CreateLogGroup', 'logs:PutLogEvents' ],
                effect: Effect.ALLOW,
                resources: ['arn:aws:logs:*:*:*']
            })
        ]
      }
  )
  
  const iam_role = new Role(
      this, 'AllowHibernateEC2InstanceFromLambdaRole',
      {
        roleName: 'AllowHibernateEC2InstanceFromLambdaRole',
        assumedBy: new ServicePrincipal('lambda.amazonaws.com')
      }
  )
  
  hibernate_policy.attachToRole(iam_role)
  
  const log_group = new LogGroup(
      this, 'HibernateEC2InstanceFunctionLogGroup',{
        logGroupName: '/aws/lambda/HibernateEC2InstanceFunction',
        removalPolicy: RemovalPolicy.DESTROY,
        retention: RetentionDays.FIVE_DAYS
      }
  )
  
  const lambda_function = new Function(
      this, 'HibernateEC2InstanceFunction',{
        functionName: 'HibernateEC2InstanceFunction',
        architecture: Architecture.ARM_64,
        code: Code.fromAsset('src/'),
        handler: 'lambda_function.lambda_handler',
        logGroup: log_group,
        role: iam_role,
        runtime: Runtime.PYTHON_3_12,
        timeout: Duration.seconds(30)
      }
  )
  
  const metric = new Metric({
      metricName: 'CPUUtilization',
      namespace: 'AWS/EC2',
      period: Duration.minutes(15),
      statistic: 'Average',
      dimensionsMap: {'InstanceId': instance_id.valueAsString}
  })
  
  const alarm = new Alarm(
      this, 'Idle-EC2-Instance-LessThan10Pct-CPUUtilization-15Min',{
      alarmName: 'Idle-EC2-Instance-LessThan10Pct-CPUUtilization-15Min',
      actionsEnabled: false,
      alarmDescription: 'Alarm on instance: Triggered when CPUUtilization >= new 0.99 for 1 consecutive 5-minute periods.',
      comparisonOperator: ComparisonOperator.LESS_THAN_THRESHOLD,
      evaluationPeriods: 1,
      metric: metric,
      threshold: 10
      }
  )
  
  const rule = new Rule(
      this, 'HibernateEC2InstanceRule',{
        ruleName: 'HibernateEC2InstanceRule',
        eventPattern: {
            source: ['aws.cloudwatch'],
            detailType: ['CloudWatch Alarm State Change'],
            detail: {'state': {'value': ['ALARM']}},
            resources: [ alarm.alarmArn ]
        }
      }
  )

  rule.addTarget(new LambdaFunction(lambda_function))
  }
}
