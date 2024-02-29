from aws_cdk import Duration, Fn, RemovalPolicy, Stack
from aws_cdk.aws_dynamodb import Attribute, AttributeType, Table
from aws_cdk.aws_ec2 import CloudFormationInit, InitCommand, InitConfig, InitFile, Instance, InstanceClass, InstanceType, MachineImage, Peer, Port, SecurityGroup, Vpc
from aws_cdk.aws_iam import Effect, ManagedPolicy, PolicyDocument, PolicyStatement, Role, ServicePrincipal
from aws_cdk.aws_lambda import Code, Function, Runtime
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from aws_cdk.aws_sqs import Queue, QueueEncryption
from constructs import Construct

class SqsTriggerLambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Messages Queue
        queue = Queue(
            self, 'MessageQueue',
            queue_name = 'Messages',
            visibility_timeout = Duration.seconds(30),
            retention_period = Duration.days(1),
            encryption = QueueEncryption.KMS_MANAGED,
            removal_policy = RemovalPolicy.DESTROY
        )
        
        # Create Lambda Role
        lambda_role = Role(
            self, 'LambdaExecutionRole',
            role_name = 'LambdaExecutionRole',
            assumed_by = ServicePrincipal('lambda.amazonaws.com'),
            managed_policies = [ 
                ManagedPolicy.from_aws_managed_policy_name('AmazonDynamoDBFullAccess'),
                ManagedPolicy.from_aws_managed_policy_name('AmazonSQSFullAccess'),
                ManagedPolicy.from_aws_managed_policy_name('AWSLambdaExecute'),
                ManagedPolicy.from_aws_managed_policy_name('CloudWatchLogsFullAccess') 
            ],
            inline_policies = {
                'root': PolicyDocument(
                    statements = [
                        PolicyStatement(
                            effect = Effect.ALLOW,
                            actions = [ "sqs:ChangeMessageVisibility", "sqs:DeleteMessage", "sqs:GetQueueAttributes", "sqs:GetQueueUrl", "sqs:ReceiveMessage"],
                            resources = [ Fn.get_att(queue.node.default_child.logical_id, 'Arn').to_string() ]
                        )
                    ]
                )
            }
        )
        
        # Stop lambda_event_source from creating a duplicate inline policy.
        lambda_role = lambda_role.without_policy_updates() 

        # Create Lambda Function to triggered by SQS
        lambda_function = Function(
            self, 'SQSDynamoDB',
            code = Code.from_asset('src/lambda'),
            handler = 'lambda_function.lambda_handler',
            runtime = Runtime.PYTHON_3_12,
            role = lambda_role,
            function_name = 'SQSDynamoDB'
        )

        # Create and add Trigger
        trigger = SqsEventSource(queue)
        lambda_function.add_event_source(trigger)

        # Create EC2 role
        ec2_role = Role(
            self, 'EC2Role',
            role_name = 'EC2Role',
            assumed_by = ServicePrincipal('amazonaws.com'),
            inline_policies = {
                'root': PolicyDocument(
                    statements = [
                        PolicyStatement(
                            effect = Effect.ALLOW,
                            actions = [ "ec2:*", "sqs:*", "cloudwatch:*", "logs:*" ],
                            resources = [ '*' ]
                        )
                    ]
                )
            }
        )

        # Create EC2 with script that adds messages to the queue.
        vpc = Vpc.from_lookup(
            self, 'VPC',
            vpc_name = 'Default VPC'
        )

        # Create Security Group
        security_group = SecurityGroup(
            self, "EC2SG",
            vpc = vpc,
            allow_all_outbound = True,
            security_group_name = 'EC2SecurityGroup'
        )
        security_group.add_ingress_rule(Peer.any_ipv4(), Port.tcp(22), 'Allow SSH traffic on Port 22')
        
        # Create EC2 Instance
        instance = Instance(
            self, 'EC2CreateMessage',
            instance_name = 'GenerateMessage',
            instance_type = InstanceType('t3.micro'),
            machine_image = MachineImage.latest_amazon_linux2(),
            vpc = vpc,
            init = CloudFormationInit.from_config_sets(
                config_sets = {
                    'default': ['setup_environment']
                },
                configs = {
                    'setup_environment': InitConfig([
                        InitCommand.shell_command('sudo yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel python3', key = '01_install_errthang'),
                        InitCommand.shell_command('python3 -m pip install boto3', key = '02_install_boto3'),
                        InitCommand.shell_command('python3 -m pip install faker', key = '03_install_faker'),
                        InitFile.from_asset('/home/ec2-user/send_message.py', 'src/ec2/send_message.py', mode = '655', owner = 'ec2-user', group = 'ec2-user')
                    ])
                }
            ),
            role = ec2_role,
            security_group = security_group
        )

        # Create DynamoDB Table
        table = Table(
            self, 'MessageTable',
            partition_key = Attribute(
                name = 'MessageId',
                type = AttributeType.STRING
            ),
            table_name = 'Messages',
            removal_policy = RemovalPolicy.DESTROY
        )

