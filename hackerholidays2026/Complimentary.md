Day 3 | Easy • Cloud • IAM Misconfiguration

The challenge provided an Amazon S3 website endpoint. Inspecting the browser's Network tab revealed requests to Amazon Cognito Identity and Amazon DynamoDB. The Cognito response exposed temporary AWS credentials, while the DynamoDB request revealed the target table name.

The credentials were configured in the terminal using the AWS CLI:

export AWS_ACCESS_KEY_ID="<ACCESS_KEY_ID>"
export AWS_SECRET_ACCESS_KEY="<SECRET_ACCESS_KEY>"
export AWS_SESSION_TOKEN="<SESSION_TOKEN>"
export AWS_DEFAULT_REGION="us-east-1"

The active AWS identity was verified using: aws sts get-caller-identity

The DynamoDB table was then queried using: aws dynamodb scan --table-name complimentary-GuestWellnessProfiles

Reviewing the table output revealed the flag, completing the challenge.
