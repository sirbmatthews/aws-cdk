import { CfnOutput, Stack, StackProps } from 'aws-cdk-lib'; 
import { CloudFormationInit, InitCommand, InitConfig, InitPackage, InitService, InitServiceRestartHandle, Instance, InstanceType, KeyPair, KeyPairFormat, MachineImage, Peer, Port, SecurityGroup, Vpc } from 'aws-cdk-lib/aws-ec2';
import { Role, ServicePrincipal } from 'aws-cdk-lib/aws-iam'; 
import { Construct } from 'constructs';


export class JenkinsServerStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

        // Lookup a VPC
        const vpc = Vpc.fromLookup(this, 'VPC', {isDefault: true})

        // Creating a key pair
        const jenkins_key_pair = new KeyPair(
            this, 'KeyPair', {
              keyPairName: 'JenkinsKeyPair',
              format: KeyPairFormat.PEM
            }
        )

        // Create a Security Group
        const jenkins_sg = new SecurityGroup(
            this, 'JenkinsSeurityGroup', {
              vpc: vpc,
              securityGroupName: 'JenkinsSecurityGroup',
            }
        )

        jenkins_sg.addIngressRule(
            Peer.anyIpv4(),
            Port.tcp(22),
            'Allow SSH conenction on Port 22'
        )

        jenkins_sg.addIngressRule(
            Peer.anyIpv4(),
            Port.tcp(8080),
            'Allow HTTP conenction on Port 8080'
        )

        // Create instance role and SSM Managed Policy
        const instance_role = new Role(
            this, 'InstanceRole', {
              assumedBy: new ServicePrincipal('ec2.amazonaws.com'),
              roleName: 'JenkinsRole'
            }
        )

        // Launching an Amazon EC2 instance
        const jenkins_instance = new Instance(
            this, 'JenkinsEC2Instance',
            {
              instanceName: 'JenkinsEC2Instance',
              instanceType: new InstanceType('t3.micro'),
              keyPair: jenkins_key_pair,
              machineImage: MachineImage.latestAmazonLinux2(),
              securityGroup: jenkins_sg,
              vpc: vpc,
              role: instance_role,
              init: CloudFormationInit.fromConfigSets({
                  configSets: { 
                      default: ['jenkinsConfig', 'install_jenkins', 'enable_service']
                  },
                  configs:{
                      'jenkinsConfig': new InitConfig([
                          InitPackage.yum('java-17-amazon-corretto'),
                          InitPackage.yum('java-1.8.0-openjdk'),
                          InitPackage.yum('java-1.8.0-openjdk-devel'),
                          InitPackage.yum('wget'),     
                          InitCommand.shellCommand('wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo', {key: '01_downloaod_jenkins_repo'}),
                          InitCommand.shellCommand('yum clean all', {key: '02_yum_clean'}),
                          InitCommand.shellCommand('rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key', {key: '03_import_jenkins_repo'}),
                          InitCommand.shellCommand('mkdir -p /home/jenkins /var/lib/jenkins/.ssh /var/cache/jenkins/war /var/log/jenkins', {key: '04_jenkins_directories'}),
                          InitCommand.shellCommand('yum upgrade -y', {key: '05_upgrade_yum'}),
                      ]),
                      'install_jenkins': new InitConfig([
                          InitPackage.yum('jenkins')
                      ]),
                      'enable_service': new InitConfig([
                          InitService.enable('jenkins', {serviceRestartHandle: new InitServiceRestartHandle()})
                      ])
                  }
              })
            }
        )
        new CfnOutput(this, 'JenkinsUrl', { value: 'https://' + jenkins_instance.instancePublicDnsName + ':8080' })
        new CfnOutput(this, 'PublicIP', { value: jenkins_instance.instancePublicIp })
  }
}
