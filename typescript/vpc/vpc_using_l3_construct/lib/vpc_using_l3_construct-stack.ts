import { Stack, StackProps, Tags } from 'aws-cdk-lib';
import { DefaultInstanceTenancy, IpAddresses, RouterType, SubnetConfiguration, SubnetType, Vpc } from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';


export class VpcStack extends Stack {
	constructor(scope: Construct, id: string, props?: StackProps) {
		super(scope, id, props);

		//  Create VPC
		const vpc = new Vpc(
			this, 'VPC', {
			ipAddresses: IpAddresses.cidr('10.0.0.0/16'),
			enableDnsHostnames: true,
			enableDnsSupport: true,
			defaultInstanceTenancy: DefaultInstanceTenancy.DEFAULT,
			restrictDefaultSecurityGroup: false,
			subnetConfiguration: [
				// Createa Public Subnet
				{
					name: 'Public',
					subnetType: SubnetType.PUBLIC,
					cidrMask: 19,
					mapPublicIpOnLaunch: true
				},
				// Createa Private Subnet
				{
					name: 'Private',
					subnetType: SubnetType.PRIVATE_WITH_EGRESS,
					cidrMask: 19
				}
			],
			// Set the number of NAT Gateways
			natGateways: 1,
			}
		)

		// Add Tags to VPC
		Tags.of(vpc).add('Name', 'VPC')
		
		// Add Tags to Private Subnets and route
		let subnet_list = vpc.selectSubnets({subnetType: SubnetType.PRIVATE_WITH_EGRESS})
		subnet_list.subnets.forEach((subnet, i) => {
			Tags.of(subnet).add('Name', 'PrivateSubnet' + (i+1).toString())
		});
		
		// Add Tags to Public Subnets and route
		subnet_list = vpc.selectSubnets({subnetType: SubnetType.PUBLIC})
		subnet_list.subnets.forEach((subnet, i) => {
			Tags.of(subnet).add('Name', 'PublicSubnet' + (i+1).toString())
		});

	}
}
