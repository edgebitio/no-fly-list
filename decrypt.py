import base64
import json
import os

import boto3
from cryptography.fernet import Fernet

def decrypt_envelope(envelope):

  # Get a KMS client
  # Check if the enclave's KMS proxy is configured
  if(os.environ.get('AWS_KMS_ENDPOINT')):
    client = boto3.client("kms", endpoint_url=os.environ.get('AWS_KMS_ENDPOINT'))
  else:
    client = boto3.client("kms");

  # Decrypt the data key from the data_key column
  decrypted_key = client.decrypt(CiphertextBlob=base64.b64decode(envelope["data-key-ciphertext-base64"]))

  # Encode decrypted key to base64
  plain_data_key = base64.b64encode(decrypted_key['Plaintext'])

  # Use the plaintext key to decrypt the user name data
  f = Fernet(plain_data_key)
  plaintext = f.decrypt(envelope["aes-ciphertext-base64"].encode())

  return plaintext.decode().split(',')

# Fetch the encrypted No-Fly list stored in a file
encrypted_envelope = json.load(open('no-fly-envelope.json'))

# Decrypt the No-Fly list
# Enclaver will attach the cryptographic attestation of this enclave to the request
# The KMS key has an access policy that explictly allows this attestation access to the key
plaintext_nofly_list = decrypt_envelope(encrypted_envelope)

print(','.join(plaintext_nofly_list))
