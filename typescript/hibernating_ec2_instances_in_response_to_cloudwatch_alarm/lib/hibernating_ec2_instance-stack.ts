import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { CfnCreationPolicy, CfnOutput, CfnParameter, CfnResourceSignal, CfnTag, Fn, Stack, StackProps } from 'aws-cdk-lib'
import { CfnInstance, UserData } from 'aws-cdk-lib/aws-ec2'

export class HibernatingEc2InstanceStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const ami = new CfnParameter(
        this, 'ImageId', {
            default: '/aws/service/ami-amazon-linux-latest/amzn2-ami-kernel-5.10-hvm-x86_64-gp2',
            type: 'AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>'
        }
    )

    const user_data = UserData.forLinux()
    user_data.addCommands('yum update -y aws-cfn-bootstrap')
    user_data.addCommands(
        '/opt/aws/bin/cfn-signal -e $? --stack ' + Fn.ref('AWS::StackName') + ' --resource HibernatingEc2Instance --region ' + Fn.ref('AWS::Region')
                           );
            
    const ec2_instance = new CfnInstance(
        this, 'HibernatingEc2Instance', {
            blockDeviceMappings: [{
                deviceName: '/dev/xvda',
                ebs:{
                    encrypted: true,
                    deleteOnTermination: true,
                    volumeSize: 8
                }
            }],
            hibernationOptions: {configured: true},
            instanceType: 't3.micro',
            imageId: Fn.ref(ami.logicalId),
            userData: Fn.base64(user_data.render()),
            tags: [{
                    key: 'Name',
                    value: 'linux-hibernate'
            }]
        }
        
    )
    
    ec2_instance.cfnOptions.creationPolicy = {resourceSignal: {count: 1, timeout: 'PT5M'}}
    
    new CfnOutput(
        this, 'HibernatingEc2InstanceOutput', {
            value: Fn.ref(ec2_instance.logicalId)
        }
    )


  }
}
