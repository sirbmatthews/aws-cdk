import { Duration, RemovalPolicy, Stack, StackProps } from 'aws-cdk-lib';
import { LogGroup, RetentionDays } from 'aws-cdk-lib/aws-logs';
import { Attribute, AttributeType, Table } from 'aws-cdk-lib/aws-dynamodb';
import { CloudFormationInit, InitCommand, InitConfig, InitFile, Instance, InstanceType, MachineImage, Peer, Port, SecurityGroup, Vpc } from 'aws-cdk-lib/aws-ec2';
import { Code, Function, Runtime } from 'aws-cdk-lib/aws-lambda';
import { SqsEventSource } from 'aws-cdk-lib/aws-lambda-event-sources';
import { Queue, QueueEncryption } from 'aws-cdk-lib/aws-sqs';
import { Construct } from 'constructs';

export class SqsTriggerLambdaStack extends Stack {
	constructor(scope: Construct, id: string, props?: StackProps) {
		super(scope, id, props);

		// Create Messages Queue
		const queue = new Queue(
			this, 'MessageQueue',
			{
				queueName: 'Messages',
				visibilityTimeout: Duration.seconds(30),
				retentionPeriod: Duration.days(1),
				encryption: QueueEncryption.KMS_MANAGED,
				removalPolicy: RemovalPolicy.DESTROY
			}
		)

		// Create Lambda Log Group
		const log_group = new LogGroup(
			this, 'LambdaLogGroup',
			{
				logGroupName: '/aws/lambda/SQSDynamoDB',
				retention: RetentionDays.ONE_DAY,
				removalPolicy: RemovalPolicy.DESTROY
			}
		)

		// Create Lambda Function to triggered by SQS
		const lambda_function = new Function(
			this, 'SQSDynamoDB',
			{
				code: Code.fromAsset('src/lambda'),
				handler: 'lambda_function.lambda_handler',
				runtime: Runtime.PYTHON_3_12,
				functionName: 'SQSDynamoDB',
				logGroup: log_group
			}
		)

		// Create and add Trigger
		const trigger = new SqsEventSource(queue)
		lambda_function.addEventSource(trigger)

		// Lookup a VPC
		const vpc = Vpc.fromLookup(this, 'VPC', { isDefault: true })

		// Create Security Group
		const security_group = new SecurityGroup(
			this, "EC2SG",
			{
				vpc: vpc,
				allowAllOutbound: true,
				securityGroupName: 'EC2SecurityGroup'
			}
		)
		security_group.addIngressRule(Peer.anyIpv4(), Port.tcp(22), 'Allow SSH traffic on Port 22')


		// Create EC2 with script that adds messages to the queue.
		const instance = new Instance(
			this, 'EC2CreateMessage',
			{
				instanceName: 'GenerateMessage',
				instanceType: new InstanceType('t3.micro'),
				machineImage: MachineImage.latestAmazonLinux2(),
				vpc: vpc,
				init: CloudFormationInit.fromConfigSets(
					{
						configSets: {
							'default': ['setup_environment']
						},
						configs: {
							'setup_environment': new InitConfig([
								InitCommand.shellCommand('sudo yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel python3', {key: '01_install_errthang'}),
								InitCommand.shellCommand('python3 -m pip install boto3', {key: '02_install_boto3'}),
								InitCommand.shellCommand('python3 -m pip install faker', {key: '03_install_faker'}),
								InitFile.fromAsset('/home/ec2-user/send_message.py', 'src/ec2/send_message.py', {mode: '655', owner: 'ec2-user', group: 'ec2-user'})
							])
						}
					}
				),
				securityGroup: security_group}
		)

		// Create DynamoDB Table
		const table = new Table(
			this, 'MessageTable',
			{
				partitionKey: {
					name: 'MessageId',
					type: AttributeType.STRING
				},
				tableName: 'Messages',
				removalPolicy: RemovalPolicy.DESTROY
			}
		)

		log_group.grantWrite(lambda_function)
		queue.grantConsumeMessages(lambda_function)
		table.grantWriteData(lambda_function)
		queue.grantSendMessages(instance)

	}
}
