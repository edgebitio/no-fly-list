import json
import base64
import sys
import boto3
from cryptography.fernet import Fernet

def encrypt_envelope(plaintext):
  # Get a KMS client
  client = boto3.client("kms")

  # Generate a new data key
  response = client.generate_data_key(KeyId="mrk-39c14bd4d71f40e390fc158fab0697dd", KeySpec="AES_256")

  # The response includes both plaintext and encrypted versions of the data key
  plain_data_key = base64.b64encode(response["Plaintext"])
  encrypted_data_key = base64.b64encode(response["CiphertextBlob"])

  # Use the plaintext key to encrypt our data, and then throw it away
  f = Fernet(plain_data_key)
  crypted = f.encrypt(bytes(plaintext, 'utf-8'))

  return {
    "data-key-ciphertext-base64": encrypted_data_key.decode(),
    "aes-ciphertext-base64": crypted.decode()
  }

def main():
  # Read the list
  plaintext_list = sys.stdin.read()

  # Encrypt an envelope
  encrypted_envelope = encrypt_envelope(plaintext_list)

  # Write to stdout
  json.dump(encrypted_envelope, sys.stdout)

if __name__ == '__main__':
    main()
