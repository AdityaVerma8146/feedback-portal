# Serverless Student Feedback Portal on AWS

Architecture: CloudFront + S3 (frontend) -> API Gateway -> Lambda (Python) -> DynamoDB, with SNS email alerts,
IAM least-privilege roles and a CloudWatch alarm. Everything is defined in `template.yaml` (Infrastructure as Code).

## Deploy (AWS CLI + SAM CLI configured)
1. `sam build`
2. `sam deploy --guided`   (stack name: feedback-portal, enter your email for NotificationEmail, region ap-south-1)
3. Confirm the SNS subscription email that AWS sends you.
4. Copy the `ApiUrl` output into `frontend/index.html` (`API_URL`).
5. `aws s3 sync frontend/ s3://<BucketName output>/`
6. Open the `WebsiteUrl` output in a browser.

## Clean up (avoid charges)
`aws s3 rm s3://<BucketName> --recursive` then `sam delete`
