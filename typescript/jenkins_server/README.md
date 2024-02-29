# Create EC2 Instance and install Jenkins Server in an existing Default VPC

This project demonstrates how to:

* Lookup an existing default VPC.
* Create an EC2 instance running Jenkins.
* Create a Security Group that allows SSH traffic in port 22 and HTTP in port 8080.
* Create a Key Pair to allow SSH connection to the instance.
* Create an Instance Role 

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `npx cdk deploy`  deploy this stack to your default AWS account/region
* `npx cdk diff`    compare deployed stack with current state
* `npx cdk synth`   emits the synthesized CloudFormation template
