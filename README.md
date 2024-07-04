# swo-summaraize-webhook-lambda

#### This is the SummarAIze lambda function which accepts GitHub webhook events for a pull request and adds a description to it.

### Installation

To run SummarAIze, the following services are required:

* AWS Lambda
* AWS API Gateway

All the required AWS resources are created with a
CloudFormation [script](summaraize-cloudformation-template.yaml).

In order to run the script, you will need:

* Python installed - you can download it from [here](https://www.python.org/downloads/).
* boto3 - The Python AWS SDK. Once you have installed Python, run `pip install boto3`.
* Node installed - you can download it from [here](https://nodejs.org/en/download).

After you have installed Python and Node, you should add the following environment variables
to your machine:

* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY
* AWS_SESSION_TOKEN - needed only if assuming a different role than the default AWS one in
  your `.aws/credentials` folder
* AWS_DEFAULT_REGION - e.g. `us-east-1`.

To obtain the first three variables, you can use the `assume-role` command,
e.g. `aws sts assume-role --role-arn <AWS_PROFILE_ARN> --role-session-name <AWS_PROFILE_NAME>`,
where `<AWS_PROFILE_ARN>` is the arn of the profile you want to assume, and the `<AWS_PROFILE_NAME>`
is the name you want to give to your assumed profile.

If you have troubles running this command, try
deleting the existing values for the `AWS_ACCESS_KEY_ID` `AWS_SECRET_ACCESS_KEY`
and `AWS_SESSION_TOKEN`
or running the command with the `--profile default` parameter.

You can also use `awsume` command to directly change to your desired AWS profile - you can install
it from [here](https://awsu.me/general/quickstart.html).

### Prerequisites

A GitHub App is required for authorizing the Lambda function. When creating the app, add the
following permissions to
it:

* Commit statuses - read and write
* Contents - read and write
* Pull requests - read and write
* Webhooks - read only
* Metadata - read only

### Running the script

Once everything is set up, navigate to the `scripts` folder and run
the [deploy-cloudformation.py](scripts/deploy-cloudformation.py) script
with `python deploy-cloudformation.py`

You will be prompted to input the following parameters:

* Github App secrets (required):
    * App Id
    * Client Id
    * Client Secret
    * Installation Id
    * Private Key - Make sure to paste the key as one line, with the `\n` character used for the new
      lines in the key.
      E.g. `-----BEGIN RSA PRIVATE KEY-----\nABCDEFGHIKLMNOPQRSTVXYZABCDEFGHIKLMNOPQRSTVXYZABCDEFGHIKLMNOPQRS\nTUV`
* API Key (required) - The API Key used for authentication. You can set this to an existing key if
  you want to. If you want to create a new key, you can do so by opening the AWS API Gateway console
  and navigating to *API keys->Create API key*. The key does not have to be attached to the created
  API for the webhook, you only need its value.
* GitHub Organization Name (required)
* Lambda function Name - The name of the Lambda function for handling webhook events (optional -
  default value: GitHubWebhookLambdaFunction)
* S3 Bucket name - The name of the S3 bucket where the lambda code will be stored. If the bucket
  does not exist it will be created. (optional - default value:
  summaraize-lambda-code)
* API Gateway name - The name of the API Gateway API (optional - default value: GitHubWebhookApi)
* API stage name - The name of the stage for the API (optional - default value: summaraize)
* CloudFormation stack name - The name of the AWS CloudFormation Stack (optional - default value:
  SummarAIzeStack)

### Creating the webhook

After you have created the AWS CloudFormation Stack, navigate to AWS API Gateway and go to
*APIs->`YOUR_API_NAME`->Stages->`YOUR_API_STAGE_NAME/api/webhook`->POST*. There you will find the
*Invoke URL* for the API. Copy it.

Open GitHub and go to the repository where you want to add SummarAIze. Go to the *Settings* page and
then the *Webhooks* tab. Click on *Add Webhook*. Input the required parameters:

* Payload URL - Your API Invoke URL.
* Content type - `application/json`
* Secret - Your API Key.
* Events - Click on *Let me select individual events.* and select only the *Pull requests* option.

Add the webhook.

#### Now everything should be set up and SummarAIze will add a description to your pull requests.
