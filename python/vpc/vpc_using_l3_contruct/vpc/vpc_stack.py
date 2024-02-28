from aws_cdk import Stack, Tags
from aws_cdk.aws_ec2 import DefaultInstanceTenancy, IpAddresses, RouterType, SubnetConfiguration, SubnetType, Vpc
from constructs import Construct

class VpcL3Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #  Create VPC
        vpc = Vpc(
            self, 
            'VPC', 
            ip_addresses = IpAddresses.cidr('10.0.0.0/16'),
            enable_dns_hostnames = True,
            enable_dns_support = True,
            default_instance_tenancy = DefaultInstanceTenancy.DEFAULT,

            subnet_configuration = [ 
                
                # Createa Public Subnet
                SubnetConfiguration(
                    name = 'Public',
                    subnet_type = SubnetType.PUBLIC,
                    cidr_mask =19, 
                    map_public_ip_on_launch = True
                ),

                # Create Private Subnet
                SubnetConfiguration(
                    name = 'Private',
                    subnet_type = SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask = 19
                )
            ],
            
            # Set the number of NAT Gateways
            nat_gateways = 1,
        )
        
        # Add Tags to VPC
        Tags.of(vpc).add('Name', 'VPC')

        # Add Tags to Private Subnets and route
        subnet_list = vpc.select_subnets(subnet_type=SubnetType.PRIVATE_WITH_EGRESS)
        for i, subnet in enumerate(subnet_list.subnets):
            Tags.of(subnet).add('Name', 'PrivateSubnet' + str(i + 1))
        
        # Add Tags to Public Subnets and route
        subnet_list = vpc.select_subnets(subnet_type=SubnetType.PUBLIC)
        for i, subnet in enumerate(subnet_list.subnets):
            Tags.of(subnet).add('Name', 'PublicSubnet' + str(i + 1))