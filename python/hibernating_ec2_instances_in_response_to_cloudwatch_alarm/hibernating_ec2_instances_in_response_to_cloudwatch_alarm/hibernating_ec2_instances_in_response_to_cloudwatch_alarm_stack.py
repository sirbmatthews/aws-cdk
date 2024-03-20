from constructs import Construct
from aws_cdk import CfnParameter, Duration, Fn, RemovalPolicy, Stack
from aws_cdk.aws_cloudwatch import Alarm, ComparisonOperator, Metric
from aws_cdk.aws_events import EventPattern, Rule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_iam import Effect, Policy, PolicyStatement, Role, ServicePrincipal
from aws_cdk.aws_lambda import Architecture, Code, Function, Runtime
from aws_cdk.aws_logs import LogGroup, RetentionDays

class HibernatingEc2InstancesInResponseToCloudwatchAlarmStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        instance_id = CfnParameter(
            self, 'InstanceId',
            description = 'Instance Id of the EC2 instance to be monitored',
            type = 'String'
        )
        
        iam_policy = Policy(
            self, 'AllowHibernateEC2InstancePolicy',
            policy_name = 'AllowHibernateEC2InstancePolicy',
            statements = [
                PolicyStatement(
                    actions = ['ec2:Stop*'],
                    effect = Effect.ALLOW,
                    resources = ['*']
                ),
                PolicyStatement(
                    actions = [ 'logs:CreateLogStream', 'logs:CreateLogGroup', 'logs:PutLogEvents' ],
                    effect = Effect.ALLOW,
                    resources = ['arn:aws:logs:*:*:*']
                )
            ]
        )
        
        iam_role = Role(
            self, 'AllowHibernateEC2InstanceFromLambdaRole',
            role_name = 'AllowHibernateEC2InstanceFromLambdaRole',
            assumed_by = ServicePrincipal('lambda.amazonaws.com')
        )
        
        iam_policy.attach_to_role(iam_role)
        
        log_group = LogGroup(
            self, 'HibernateEC2InstanceFunctionLogGroup',
            log_group_name = '/aws/lambda/HibernateEC2InstanceFunction',
            removal_policy = RemovalPolicy.DESTROY,
            retention = RetentionDays.FIVE_DAYS
        )
        
        lambda_function = Function(
            self, 'HibernateEC2InstanceFunction',
            function_name = 'HibernateEC2InstanceFunction',
            architecture = Architecture.ARM_64,
            code = Code.from_asset('src/'),
            handler = 'lambda_function.lambda_handler',
            log_group = log_group,
            role = iam_role,
            runtime = Runtime.PYTHON_3_12,
            timeout = Duration.seconds(30)
        )
        
        metric = Metric(
            metric_name = 'CPUUtilization',
            namespace = 'AWS/EC2',
            period = Duration.minutes(15),
            statistic = 'Average',
            dimensions_map = {'InstanceId': instance_id.value_as_string}
        )
        
        alarm = Alarm(
            self, 'Idle-EC2-Instance-LessThan10Pct-CPUUtilization-15Min',
            alarm_name = 'Idle-EC2-Instance-LessThan10Pct-CPUUtilization-15Min',
            actions_enabled = False,
            alarm_description = 'Alarm on instance: Triggered when CPUUtilization >= 0.99 for 1 consecutive 5-minute periods.',
            comparison_operator = ComparisonOperator.LESS_THAN_THRESHOLD,
            evaluation_periods = 1,
            metric = metric,
            threshold = 10
        )
        
        rule = Rule(
            self, 'HibernateEC2InstanceRule',
            rule_name = 'HibernateEC2InstanceRule',
            event_pattern = EventPattern(
                source = ['aws.cloudwatch'],
                detail_type = ['CloudWatch Alarm State Change'],
                detail = {'state': {'value': ['ALARM']}},
                resources = [ alarm.alarm_arn ]
            ),
        )

        rule.add_target(LambdaFunction(lambda_function))
        