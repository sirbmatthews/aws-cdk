from aws_cdk import CfnOutput, Stack
from aws_cdk.aws_ec2 import CloudFormationInit, InitCommand, InitConfig, InitPackage, InitService, InitServiceRestartHandle, Instance, InstanceType, KeyPair, KeyPairFormat, MachineImage, Peer, Port, SecurityGroup, Vpc
from aws_cdk.aws_iam import  Role, ServicePrincipal
from constructs import Construct

class JenkinsServerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lookup a VPC
        vpc = Vpc.from_lookup(self, 'VPC', is_default = True)

        # Creating a key pair
        jenkins_key_pair = KeyPair(
            self, 'KeyPair',
            key_pair_name = 'JenkinsKeyPair',
            format = KeyPairFormat.PEM, 
        )

        # Create a Security Group
        jenkins_sg = SecurityGroup(
            self, 'JenkinsSeurityGroup',
            vpc = vpc,
            security_group_name = 'JenkinsSecurityGroup',
        )

        jenkins_sg.add_ingress_rule(
            peer = Peer.any_ipv4(),
            connection = Port.tcp(22),
            description = 'Allow SSH conenction on Port 22'
        )

        jenkins_sg.add_ingress_rule(
            peer = Peer.any_ipv4(),
            connection = Port.tcp(8080),
            description = 'Allow HTTP conenction on Port 8080'
        )

        # Create instance role and SSM Managed Policy
        instance_role = Role(
            self, 'InstanceRole',
            assumed_by = ServicePrincipal('ec2.amazonaws.com'),
            role_name = 'JenkinsRole'
        )

        # Launching an Amazon EC2 instance
        jenkins_instance = Instance(
            self, 'JenkinsEC2Instance',
            instance_name = 'JenkinsEC2Instance',
            instance_type = InstanceType('t3.micro'),
            key_pair = jenkins_key_pair,
            machine_image = MachineImage.latest_amazon_linux2(),
            security_group = jenkins_sg,
            vpc = vpc,
            role = instance_role,
            init = CloudFormationInit.from_config_sets(
                config_sets = { 
                    'default': ['jenkinsConfig', 'install_jenkins', 'enable_service']
                },
                configs={
                    'jenkinsConfig': InitConfig([
                        InitPackage.yum('java-17-amazon-corretto'),
                        InitPackage.yum('java-1.8.0-openjdk'),
                        InitPackage.yum('java-1.8.0-openjdk-devel'),
                        InitPackage.yum('wget'),     
                        InitCommand.shell_command(key = '01_downloaod_jenkins_repo', shell_command = 'wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo'),
                        InitCommand.shell_command(key = '02_yum_clean', shell_command = 'yum clean all'),
                        InitCommand.shell_command(key = '03_import_jenkins_repo', shell_command = 'rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key'),
                        InitCommand.shell_command(key = '04_jenkins_directories', shell_command = 'mkdir -p /home/jenkins /var/lib/jenkins/.ssh /var/cache/jenkins/war /var/log/jenkins'),
                        InitCommand.shell_command(key = '05_upgrade_yum', shell_command = 'yum upgrade -y'),
                    ]),
                    'install_jenkins': InitConfig([
                        InitPackage.yum('jenkins')
                    ]),
                    'enable_service': InitConfig([
                        InitService.enable('jenkins', service_restart_handle = InitServiceRestartHandle())
                    ])
                }
            )
        )
        
        CfnOutput(self, 'JenkinsUrl', value = 'https://' + jenkins_instance.instance_public_dns_name + ':8080')
        CfnOutput(self, 'PublicIP', value = jenkins_instance.instance_public_ip)