from aws_cdk import Stack, CfnTag, Fn
from aws_cdk.aws_ec2 import CfnVPC, CfnSubnet, CfnRouteTable, CfnSubnetRouteTableAssociation, CfnInternetGateway, CfnVPCGatewayAttachment, CfnRoute, CfnEIP, CfnNatGateway
from constructs import Construct

class VpcStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

         # Variables
        base_path = '/' + self.stack_name + '/' + self.region + '/'
        
         #  Create VPC
        vpc = CfnVPC(
            self,
            "VPC",
            cidr_block = '10.0.0.0/16',
            enable_dns_hostnames = True,
            enable_dns_support = True,
            instance_tenancy = 'default',
            tags = [CfnTag(key = 'Name', value = 'ApplicationVPC')]
        )
        
        # Subnets variables
        public_subnet_cidr = ['10.0.0.0/20', '10.0.4.0/20', '10.0.8.0/20']
        private_subnet_cidr = ['10.0.12.0/20', '10.0.16.0/20', '10.0.20.0/20']
        iso_private_subnet_cidr = ['10.0.24.0/20', '10.0.28.0/20', '10.0.32.0/20']
        public_subnets = []
        private_subnets = []
        iso_private_subnets = []

        # Create Public Subnets
        for i, cidr in enumerate(public_subnet_cidr):
            public_subnets.append(
                CfnSubnet(
                    self,
                    "PublicSubnet" + str(i+1),
                    availability_zone = Fn.select(i, Fn.get_azs()),
                    cidr_block = cidr,
                    vpc_id = vpc.attr_vpc_id,
                    map_public_ip_on_launch = True,
                    tags = [CfnTag(key = 'Name', value = 'PublicSubnet' + str(i+1)), CfnTag(key = 'Type', value = 'Public')]
                )
            )
        # Create Private Subnets
        for i, cidr in enumerate(private_subnet_cidr):
            private_subnets.append(
                CfnSubnet(
                    self,
                    "PrivateSubnet" + str(i+1),
                    availability_zone = Fn.select(i, Fn.get_azs()),
                    cidr_block = cidr,
                    vpc_id = vpc.attr_vpc_id,
                    map_public_ip_on_launch = True,
                    tags = [CfnTag(key = 'Name', value = 'PrivateSubnet' + str(i+1)), CfnTag(key = 'Type', value = 'Private')]
                )
            )
            
        # Create Isolated Private Subnets
        for i, cidr in enumerate(iso_private_subnet_cidr):
            iso_private_subnets.append(
                CfnSubnet(
                    self,
                    "IsoPrivateSubnet" + str(i+1),
                    availability_zone = Fn.select(i, Fn.get_azs()),
                    cidr_block = cidr,
                    vpc_id = vpc.attr_vpc_id,
                    tags = [CfnTag(key = 'Name', value = 'IsoPrivateSubnet' + str(i+1)), CfnTag(key = 'Type', value = 'Isolated')]
                )
            )
        
        # Create Public Route Table
        public_route_table = CfnRouteTable(
            self,
            'PublicRouteTable',
            vpc_id = vpc.attr_vpc_id,
            tags = [CfnTag(key = 'Name', value = 'PublicRouteTable')]
        )

        # Create Private Route Table
        private_route_table = CfnRouteTable(
            self,
            'PrivateRouteTable',
            vpc_id = vpc.attr_vpc_id,
            tags = [CfnTag(key = 'Name', value = 'PrivateRouteTable')]
        )

        # Create Isolated Private Route Table
        iso_private_route_table = CfnRouteTable(
            self,
            'IsoPrivateRouteTable',
            vpc_id = vpc.attr_vpc_id,
            tags = [CfnTag(key = 'Name', value = 'IsoPrivateRouteTable')]
        )

        # Create Public Subnet Route Table Associations
        for i, subnet in enumerate(public_subnets):
            CfnSubnetRouteTableAssociation(
                self,
                'PublicSubnetRouteTableAssociation' + str(i+1),
                route_table_id = public_route_table.attr_route_table_id,
                subnet_id = subnet.attr_subnet_id
            )
            
        # Create Private Subnet Route Table Associations
        for i, subnet in enumerate(private_subnets):
            CfnSubnetRouteTableAssociation(
                self,
                'PrivateSubnetRouteTableAssociation' + str(i+1),
                route_table_id = private_route_table.attr_route_table_id,
                subnet_id = subnet.attr_subnet_id
            )
            
        # Create Isolated Private Subnet Route Table Associations
        for i, subnet in enumerate(iso_private_subnets):
            CfnSubnetRouteTableAssociation(
                self,
                'IsolatedPrivateSubnetRouteTableAssociation' + str(i+1),
                route_table_id = iso_private_route_table.attr_route_table_id,
                subnet_id = subnet.attr_subnet_id
            )

        # Create Internet Gateway 
        internet_gateway = CfnInternetGateway(
            self,
            'InternetGateway',
            tags = [CfnTag(key = 'Name', value = 'InternetGateway')]
        )
        
        # Create Route for Internet Gateway
        routeIGW = CfnRoute(
            self,
            'RouteIGW',
            route_table_id = public_route_table.attr_route_table_id,
            destination_cidr_block = '0.0.0.0/0',
            gateway_id = internet_gateway.attr_internet_gateway_id
        )


        # Create VPC Internet Gateway Attachment
        vpc_gateway_attachment = CfnVPCGatewayAttachment(
            self,
            'VPCInternetGatewayAttachment',
            internet_gateway_id = internet_gateway.attr_internet_gateway_id,
            vpc_id = vpc.attr_vpc_id
        )

        # Create EIP
        eip = CfnEIP(
            self,
            'ElasticIP',
            domain = 'vpc',
            tags = [CfnTag(key = 'Name', value = 'ElasticIP')]
        )

        # Create NAT Gateway
        nat_gateway = CfnNatGateway(
            self, 
            'NATGateway',
            subnet_id = public_subnets[0].attr_subnet_id,
            allocation_id = eip.attr_allocation_id,
            tags = [CfnTag(key = 'Name', value = 'NATGateway')]
        )

        # Create Route for NAT Gateway
        routeNat = CfnRoute(
            self,
            'RouteNAT',
            route_table_id = private_route_table.attr_route_table_id,
            destination_cidr_block = '0.0.0.0/0',
            nat_gateway_id = nat_gateway.attr_nat_gateway_id
        )