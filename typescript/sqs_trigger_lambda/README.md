## How to trigger a Lambda function using SQS. 
This Lambda function will process messages from the SQS queue and insert the message data as records into a DynamoDB table.


This project demonstrates how to:
* Create a Lambda Function (SQSDynamoDB)
* Create a DynamoDB Table (Messages)
* Create an SQS Queue (Messages)
* Create an SQS Trigger (SQS > Messages)
* Create the EC2 instance to run a script that generates messages and send them to the SQS
* Log In to the EC2 Instance and run the script (send_messages.py)

    ``` ./send_message.py -q Messages -i 0.1 --region <region> ```
* Cancel the script execution

    ` ctrl c`
* Confirm Messages were inserted into the DynamoDB Table (Messages)

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `npx cdk deploy`  deploy this stack to your default AWS account/region
* `npx cdk diff`    compare deployed stack with current state
* `npx cdk synth`   emits the synthesized CloudFormation template
