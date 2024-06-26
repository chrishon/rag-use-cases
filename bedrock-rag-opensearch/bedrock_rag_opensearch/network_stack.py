from aws_cdk import (
    Aws,
    Stack,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_iam as iam,
    CfnOutput,
    triggers,
)
from constructs import Construct


class NetworkingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.primary_vpc = ec2.Vpc(
            self,
            "PrimaryVPC",
            ip_addresses=ec2.IpAddresses.cidr("192.168.0.0/20"),
            availability_zones=["eu-central-1a", "eu-central-1b", "eu-central-1c"],
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=26,
                ),
            ],
            enable_dns_hostnames=True,
            enable_dns_support=True,
            nat_gateways=0,
        )

        self.primary_vpc.add_interface_endpoint(
            "BedrockEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.BEDROCK,
            subnets=ec2.SubnetSelection(
                availability_zones=["eu-central-1a", "eu-central-1b", "eu-central-1c"]
            ),
        )
        self.primary_vpc.add_interface_endpoint(
            "BedrockRuntimeEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.BEDROCK_RUNTIME,
            subnets=ec2.SubnetSelection(
                availability_zones=["eu-central-1a", "eu-central-1b", "eu-central-1c"]
            ),
        )

        CfnOutput(self, "VpcId", value=self.primary_vpc.vpc_id)

        for index, subnet in enumerate(self.primary_vpc.isolated_subnets):
            CfnOutput(self, f"PrivateSubnet{index + 1}Id", value=subnet.subnet_id)
        CfnOutput(
            self,
            "DefaultSecurityGroupID",
            value=self.primary_vpc.vpc_default_security_group,
        )
