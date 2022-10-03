# No Fly List Enclave Example App

Read the full guide to using this app at https://edgebit.com/enclaver/docs/0.x/guide-app/

The info below is just for building and testing the demo app.

## Container Images

Containers are built on merge with GitHub Actions and stored on Google:

```
us-docker.pkg.dev/edgebit-containers/containers/no-fly-list:latest
```

## Running Locally

```
docker build -t demo-enclave -f Dockerfile . && docker run --name enclave -d -p 8001:8001 -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION=us-east-1 -e PYTHONUNBUFFERED=1 --rm demo-enclave
```

## Updating the No Fly List

This is only for EdgeBit staff, who have access to update the encrypted No-Fly-List contained in the demo container.

1. Configure your AWS credentials via environment variables:

```
$ export AWS_ACCESS_KEY_ID=
$ export AWS_SECRET_ACCESS_KEY=
```

2. Populate your new list:

```
fullname,anothername
```

3. Start the container but overrride the `FLASK_APP`:

```
docker build -t demo-enclave -f Dockerfile . && docker run --name enclave -d -p 8001:8001 -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION=us-east-1 -e PYTHONUNBUFFERED=1 -e FLASK_APP=/opt/app/encrypt.py --rm demo-enclave 
```

3. Curl it to encrypt and uplaod it to S3:

```
curl -d "list=fullname,anothername" -X POST http://localhost:8001/enclave/encrypt
```