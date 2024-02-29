# Create a VPC uisng L1 construct

This project demonstrates how to:

* Create a VPC.
* Create 3 public and 3 private Subnets.
* Create public and private Route Tables.
* Create public and private Subnet Route Table Associations.
* Create Internet Gateway, Route for Internet Gateway and Internet Gateway Attachment.
* Create Elastic IP, NAT Gateway and Route for NAT Gateway.


The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `npx cdk deploy`  deploy this stack to your default AWS account/region
* `npx cdk diff`    compare deployed stack with current state
* `npx cdk synth`   emits the synthesized CloudFormation template
