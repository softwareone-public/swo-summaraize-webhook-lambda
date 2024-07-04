import os
import platform
import subprocess
import boto3
from utils import copy_files_to_parent_directory, zip_files_with_name, remove_folder_contents

cf_client = boto3.client('cloudformation')
s3_client = boto3.client('s3')

shell = False
LAMBDA_NAME = "GitHubWebhookLambdaFunction"
S3_BUCKET = "summaraize-lambda-code"
API_GATEWAY_NAME = "GitHubWebhookApi"
API_STAGE_NAME = "summaraize"
CF_STACK_NAME = "SummarAIzeStack"
ORG_NAME = ""
API_KEY = ""
GITHUB_APP_ID = ""
GITHUB_CLIENT_ID = ""
GITHUB_CLIENT_SECRET = ""
GITHUB_INSTALLATION_ID = ""
GITHUB_PK = ""
separator = ""

if platform.system() == "Windows":
    separator = "\\"
    shell = True
else:
    separator = "/"

while API_KEY == "":
    API_KEY = input("Enter API Key: ")
print()

while GITHUB_APP_ID == "":
    GITHUB_APP_ID = input("Enter GitHub App Id: ")
print()

while GITHUB_CLIENT_ID == "":
    GITHUB_CLIENT_ID = input("Enter GitHub Client Id: ")
print()

while GITHUB_CLIENT_SECRET == "":
    GITHUB_CLIENT_SECRET = input("Enter GitHub Client Secret: ")
print()

while GITHUB_INSTALLATION_ID == "":
    GITHUB_INSTALLATION_ID = input("Enter GitHub Installation Id: ")
print()

while GITHUB_PK == "":
    GITHUB_PK = input("Enter GitHub Private Key: ")
print()

while ORG_NAME == "":
    ORG_NAME = input("Enter GitHub Organization Name: ")
print()

LAMBDA_NAME = input("Enter Lambda function Name (default: GitHubWebhookLambdaFunction): ") or LAMBDA_NAME
print()
S3_BUCKET = input("Enter S3 Bucket name (default: summaraize-lambda-code): ") or S3_BUCKET
print()
API_GATEWAY_NAME = input("Enter API Gateway name (default: GitHubWebhookApi): ") or API_GATEWAY_NAME
print()
API_STAGE_NAME = input("Enter API stage name (default: summaraize): ") or API_STAGE_NAME
print()
CF_STACK_NAME = input("Enter name for the CloudFormation stack (default: SummarAIzeStack): ") or CF_STACK_NAME
print()

API_KEY_PARAMETER = "{\"API_KEY\":\"" + API_KEY + "\"}"
GITHUB_APP_ID_PARAMETER = "{\"GITHUB_APP_ID\":\"" + GITHUB_APP_ID + "\"}"
GITHUB_CLIENT_ID_PARAMETER = "{\"GITHUB_CLIENT_ID\":\"" + GITHUB_CLIENT_ID + "\"}"
GITHUB_CLIENT_SECRET_PARAMETER = "{\"GITHUB_CLIENT_SECRET\":\"" + GITHUB_CLIENT_SECRET + "\"}"
GITHUB_INSTALLATION_ID_PARAMETER = "{\"GITHUB_INSTALLATION_ID\":\"" + GITHUB_INSTALLATION_ID + "\"}"
GITHUB_PK_PARAMETER = "{\"GITHUB_PK\":\"" + GITHUB_PK + "\"}"

remove_folder_contents(separator)

subprocess.run(["npm", "install"], shell=shell)

subprocess.run(["esbuild", "src" + separator + "index.ts", "--bundle",
                "--minify", "--sourcemap", "--platform=node",
                "--target=es2021", "--outfile=dist" + separator + "index.js"], shell=shell)

copy_files_to_parent_directory("dist")

zip_files_with_name("index.js", "function.zip")

os.remove("index.js")
os.remove("index.js.map")


buckets = s3_client.list_buckets()

bucket_names = [bucket['Name'] for bucket in buckets['Buckets']]

if S3_BUCKET not in bucket_names:
    s3_client.create_bucket(Bucket=S3_BUCKET)

s3_client.upload_file(Filename='function.zip', Bucket=S3_BUCKET, Key='function.zip')


cf_client.create_stack(StackName=CF_STACK_NAME,
                       TemplateBody=open('summaraize-cloudformation-template.yaml').read(),
                       Capabilities=["CAPABILITY_NAMED_IAM"],
                       Parameters=[{'ParameterKey': "APIKeySecretValueParameter",
                                    'ParameterValue': API_KEY_PARAMETER},
                                   {'ParameterKey': "AppIDSecretParameter",
                                    'ParameterValue': GITHUB_APP_ID_PARAMETER},
                                   {'ParameterKey': "ClientIDSecretParameter",
                                    'ParameterValue': GITHUB_APP_ID_PARAMETER},
                                   {'ParameterKey': "ClientSecretSecretParameter",
                                    'ParameterValue': GITHUB_CLIENT_SECRET_PARAMETER},
                                   {'ParameterKey': "InstallationIDSecretParameter",
                                    'ParameterValue': GITHUB_INSTALLATION_ID_PARAMETER},
                                   {'ParameterKey': "PrivateKeySecretParameter",
                                    'ParameterValue': GITHUB_PK_PARAMETER},
                                   {'ParameterKey': "WebhookLambdaNameParameter",
                                    'ParameterValue': LAMBDA_NAME},
                                   {'ParameterKey': "WebhookLambdaCodeBucketParameter",
                                    'ParameterValue': S3_BUCKET},
                                   {'ParameterKey': "GitHubWebhookApiNameParameter",
                                    'ParameterValue': API_GATEWAY_NAME},
                                   {'ParameterKey': "GitHubWebhookApiStageNameParameter",
                                    'ParameterValue': API_STAGE_NAME},
                                   {'ParameterKey': "GitHubOrgNameParameter",
                                    'ParameterValue': ORG_NAME}])

print("AWS stack creation initiated.")
