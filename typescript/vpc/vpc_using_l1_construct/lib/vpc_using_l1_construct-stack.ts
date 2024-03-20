import { Fn, Stack, StackProps } from 'aws-cdk-lib';
import { CfnVPC, CfnSubnet, CfnRouteTable, CfnSubnetRouteTableAssociation, CfnInternetGateway, CfnVPCGatewayAttachment, CfnRoute, CfnEIP, CfnNatGateway } from 'aws-cdk-lib/aws-ec2';
import { Construct } from 'constructs';

export class VpcStack extends Stack {
	constructor(scope: Construct, id: string, props?: StackProps) {
		super(scope, id, props);

    	//  Create VPC
		const vpc = new CfnVPC(
			this, "VPC",{
				cidrBlock: '10.0.0.0/16',
				enableDnsHostnames: true,
				enableDnsSupport: true,
				instanceTenancy: 'default',
				tags: [
					{key: 'Name', value: 'VPC'}
				]
			}
		)
    
    	// Subnets variables
		const public_subnet_cidr = ['10.0.0.0/20', '10.0.16.0/20', '10.0.32.0/20']
        const private_subnet_cidr = ['10.0.48.0/20', '10.0.64.0/20', '10.0.80.0/20']
        const iso_private_subnet_cidr = ['10.0.96.0/20', '10.0.112.0/20', '10.0.128.0/20']
		let public_subnets = new Array()
		let private_subnets = new Array()
		let iso_private_subnets = new Array()

    	// Create Public Subnets
		public_subnet_cidr.forEach((cidr, i) => {
			public_subnets.push(
				new CfnSubnet(
					this, "PublicSubnet" + (i+1).toString(),
					{
						availabilityZone: Fn.select(i, Fn.getAzs()),
						cidrBlock: cidr,
						vpcId: vpc.attrVpcId,
						mapPublicIpOnLaunch: true,
						tags: [ {key: 'Name', value: 'PublicSubnet' + (i+1).toString()} ]
					}
				)
			)
		});

    	// Create Private Subnets
		private_subnet_cidr.forEach((cidr, i) => {
			private_subnets.push(
				new CfnSubnet(
					this, "PrivateSubnet" + (i+1).toString(),
					{
						availabilityZone: Fn.select(i, Fn.getAzs()),
						cidrBlock: cidr,
						vpcId: vpc.attrVpcId,
						mapPublicIpOnLaunch: true,
						tags: [ {key: 'Name', value: 'PrivateSubnet' + (i+1).toString()} ]
					}
				)
			)
		});

    	// Create Isolated Private Subnets
		iso_private_subnet_cidr.forEach((cidr, i) => {
			iso_private_subnets.push(
				new CfnSubnet(
					this, "IsolatedPrivateSubnet" + (i+1).toString(),
					{
						availabilityZone: Fn.select(i, Fn.getAzs()),
						cidrBlock: cidr,
						vpcId: vpc.attrVpcId,
						mapPublicIpOnLaunch: true,
						tags: [ {key: 'Name', value: 'IsolatedPrivateSubnet' + (i+1).toString()} ]
					}
				)
			)
		});

		// Create Public Route Table
		const public_route_table = new CfnRouteTable(
			this, 'PublicRouteTable',
			{
				vpcId: vpc.attrVpcId,
				tags: [ {key: 'Name', value: 'PublicRouteTable'} ]
			}	
		)

      	// Create Private Route Table
		const private_route_table = new CfnRouteTable(
			this, 'PrivateRouteTable',
			{
				vpcId: vpc.attrVpcId,
				tags: [ {key: 'Name', value: 'PrivateRouteTable'} ]
			}	
		)

		// Create Isolaed Private Route Table
		const iso_private_route_table = new CfnRouteTable(
			this, 'IsolatedPrivateRouteTable',
			{
				vpcId: vpc.attrVpcId,
				tags: [ {key: 'Name', value: 'IsolatedRouteTable'} ]
			}	
		)

    	// Create Public Subnet Route Table Associations
		public_subnets.forEach((subnet, i) => {
			new CfnSubnetRouteTableAssociation(
				this, 'PublicSubnetRouteTableAssociation' + (i+1).toString(),
				{
					routeTableId: public_route_table.attrRouteTableId,
					subnetId: subnet.attrSubnetId
				}
			)
		})

    	// Create Private Subnet Route Table Associations
		private_subnets.forEach((subnet, i) => {
			new CfnSubnetRouteTableAssociation(
				this, 'PrivateSubnetRouteTableAssociation' + (i+1).toString(),
				{
					routeTableId: private_route_table.attrRouteTableId,
					subnetId: subnet.attrSubnetId
				}
			)
		})

    	// Create Private Subnet Route Table Associations
		iso_private_subnets.forEach((subnet, i) => {
			new CfnSubnetRouteTableAssociation(
				this, 'IsolatedPrivateSubnetRouteTableAssociation' + (i+1).toString(),
				{
					routeTableId: iso_private_route_table.attrRouteTableId,
					subnetId: subnet.attrSubnetId
				}
			)
		})

    	// Create Internet Gateway
		const internet_gateway = new CfnInternetGateway(
			this, 'InternetGateway',
			{tags: [{key: 'Name', value: 'InternetGateway'}]}
		)
    
		// Create Route for Internet Gateway
		const routeIGW = new CfnRoute(
				this, 'RouteIGW',
				{
					routeTableId: public_route_table.attrRouteTableId,
					destinationCidrBlock: '0.0.0.0/0',
					gatewayId: internet_gateway.attrInternetGatewayId
				}
		)


    	// Create VPC Internet Gateway Attachment
		const vpc_gateway_attachment = new CfnVPCGatewayAttachment(
			this,
			'VPCInternetGatewayAttachment',
			{
				internetGatewayId: internet_gateway.attrInternetGatewayId,
				vpcId: vpc.attrVpcId
			}
		)

    	// Create EIP
		const eip = new CfnEIP(
			this, 'ElasticIP',
			{
				domain: 'vpc',
				tags: [{key: 'Name', value: 'ElasticIP'}]
			}
		)

    	// Create NAT Gateway
		const nat_gateway = new CfnNatGateway(
			this, 'NATGateway',
			{
				subnetId: public_subnets[0].attrSubnetId,
				allocationId: eip.attrAllocationId,
				tags: [{key: 'Name', value: 'NATGateway'}]
			}
		)

		// Create Route for NAT Gateway
		const routeNat = new CfnRoute(
			this, 'RouteNAT',
			{
				routeTableId: private_route_table.attrRouteTableId,
				destinationCidrBlock: '0.0.0.0/0',
				natGatewayId: nat_gateway.attrNatGatewayId
			}
		)
  }
}
