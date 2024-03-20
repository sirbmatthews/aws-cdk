from constructs import Construct
from aws_cdk import CfnCreationPolicy, CfnOutput, CfnParameter, CfnResourceSignal, CfnTag, Fn, Stack
from aws_cdk.aws_ec2 import CfnInstance, UserData


class HibernatingEc2InstanceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        ami = CfnParameter(
            self, 'ImageId',
            default = '/aws/service/ami-amazon-linux-latest/amzn2-ami-kernel-5.10-hvm-x86_64-gp2',
            type = 'AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>'
        )

        user_data = UserData.for_linux()
        user_data.add_commands('yum update -y aws-cfn-bootstrap')
        user_data.add_commands('/opt/aws/bin/cfn-signal -e $? '
                               f'--stack {Fn.ref('AWS::StackName')} '
                               f'--resource HibernatingEc2Instance '
                               f'--region {Fn.ref('AWS::Region')}'
                               )
                
        ec2_instance = CfnInstance(
            self, 'HibernatingEc2Instance',
            block_device_mappings = [CfnInstance.BlockDeviceMappingProperty(
                device_name = '/dev/xvda',
                ebs = CfnInstance.EbsProperty(
                    encrypted = True,
                    delete_on_termination = True,
                    volume_size = 8
                )
            )],
            hibernation_options = CfnInstance.HibernationOptionsProperty(configured = True),
            instance_type = 't3.micro',
            image_id = Fn.ref(ami.logical_id),
            user_data = Fn.base64(user_data.render()),
            tags = [
                CfnTag(
                    key = 'Name',
                    value = 'linux-hibernate'
                )
            ]
        )
        
        ec2_instance.cfn_options.creation_policy = CfnCreationPolicy(resource_signal = CfnResourceSignal(count = 1, timeout = 'PT5M'))
        
        CfnOutput(
            self, 'HibernatingEc2InstanceOutput',
            value = Fn.ref(ec2_instance.logical_id)
        )

