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
            cidr="192.168.0.0/24",
            max_azs=3,
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

        CfnOutput(self, "VpcId", value=self.primary_vpc.vpc_id)

        for index, subnet in enumerate(self.primary_vpc.isolated_subnets):
            CfnOutput(self, f"PrivateSubnet{index + 1}Id", value=subnet.subnet_id)
        CfnOutput(
            self,
            "DefaultSecurityGroupID",
            value=self.primary_vpc.vpc_default_security_group,
        )
