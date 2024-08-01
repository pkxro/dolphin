import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as fs from "fs";

const config = new pulumi.Config();
const keyName = config.require("keyName"); // AWS EC2 key pair name

// Create a VPC
const vpc = new aws.ec2.Vpc("solana-vpc", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    enableDnsSupport: true,
});

// Create an internet gateway
const internetGateway = new aws.ec2.InternetGateway("solana-gw", {
    vpcId: vpc.id,
});

// Create a route table
const routeTable = new aws.ec2.RouteTable("solana-rt", {
    vpcId: vpc.id,
    routes: [
        {
            cidrBlock: "0.0.0.0/0",
            gatewayId: internetGateway.id,
        },
    ],
});

// Create a subnet
const subnet = new aws.ec2.Subnet("solana-subnet", {
    vpcId: vpc.id,
    cidrBlock: "10.0.1.0/24",
    mapPublicIpOnLaunch: true,
});

// Associate the route table with the subnet
const routeTableAssociation = new aws.ec2.RouteTableAssociation("solana-rta", {
    subnetId: subnet.id,
    routeTableId: routeTable.id,
});

// Create a security group
const securityGroup = new aws.ec2.SecurityGroup("solana-sg", {
    description: "Allow Solana traffic",
    vpcId: vpc.id,
    ingress: [
        { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] },
        { protocol: "tcp", fromPort: 8000, toPort: 8010, cidrBlocks: ["0.0.0.0/0"] },
        { protocol: "tcp", fromPort: 8899, toPort: 8900, cidrBlocks: ["0.0.0.0/0"] },
        { protocol: "tcp", fromPort: 9900, toPort: 9900, cidrBlocks: ["0.0.0.0/0"] },
    ],
    egress: [
        { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] },
    ],
});

// Read the user data script
const userDataScript = fs.readFileSync("setup_solana.sh", "utf8");

// Create the bootstrap validator EC2 instance
const bootstrapValidator = new aws.ec2.Instance("solana-bootstrap-validator", {
    instanceType: "t3.xlarge",
    ami: "ami-0aa7d40eeae50c9a9", // Amazon Linux 2 AMI (adjust for your region)
    keyName: keyName,
    vpcSecurityGroupIds: [securityGroup.id],
    subnetId: subnet.id,
    userData: userDataScript,
    tags: {
        Name: "Solana Bootstrap Validator",
    },
});

// Create the RPC validator EC2 instance
const rpcValidator = new aws.ec2.Instance("solana-rpc-validator", {
    instanceType: "t3.xlarge",
    ami: "ami-0aa7d40eeae50c9a9", // Amazon Linux 2 AMI (adjust for your region)
    keyName: keyName,
    vpcSecurityGroupIds: [securityGroup.id],
    subnetId: subnet.id,
    userData: userDataScript,
    tags: {
        Name: "Solana RPC Validator",
    },
});

// Export the public IPs of the instances
export const bootstrapValidatorPublicIp = bootstrapValidator.publicIp;
export const rpcValidatorPublicIp = rpcValidator.publicIp;