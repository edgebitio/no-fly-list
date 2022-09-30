# No Fly List Enclave Example App

Read the full guide to using this app at https://edgebit.com/enclaver/docs/0.x/guide-app/

## Container Images

TODO: build and publish these publicly

## Running Locally

```
docker build -t demo-enclave -f Dockerfile . && docker run --name enclave -d -p 8001:8001 -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION=us-east-1 -e PYTHONUNBUFFERED=1 --rm demo-enclave
```

## Updating the No Fly List

This is only for EdgeBit staff, who have access to update the encrypted No-Fly-List contained in the demo container.

First, configure your AWS credentials via environment variables:

```
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
```

Populate your new list at no-fly.txt:

```
fullname,anothername
```

Now you can curl in a new list which will be encrypted with the KMS key and returned to you:

```
aws kms encrypt --key-id mrk-b3152356da604a7dac485a0a272957c7 --plaintext "$(cat no-fly.txt | base64)" --query CiphertextBlob --output text > no-fly-encrypted.txt
```

Then upload those contents to S3:

```
aws s3 cp no-fly-encrypted.txt s3://no-fly-list/
```