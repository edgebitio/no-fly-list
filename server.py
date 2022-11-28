import os
import json
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import base64
import boto3
from cryptography.fernet import Fernet

app = Flask(__name__)

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
  plaintext = f.decrypt(envelope["aes-ciphertext-base64"])

  return plaintext.decode().split(',')

def fetch_S3_envelope():
  s3 = boto3.resource('s3')

  # This object has a public access policy
  obj = s3.Object('edgebit-no-fly-list', 'no-fly-envelope.txt')
  return json.loads(obj.get()['Body'].read().decode('utf-8'))

# Fetch the encrypted No-Fly list stored as envelope on S3
encrypted_envelope = fetch_S3_envelope()

# Decrypt the No-Fly list
# Enclaver will attach the cryptographic attestation of this enclave to the request
# The KMS key has an access policy that explictly allows this attestation access to the key
plaintext_nofly_list = decrypt_envelope(encrypted_envelope)

@app.route('/')
def index():
  return jsonify("https://edgebit.io/enclaver/docs/0.x/guide-app/")

@app.route('/enclave/passenger', methods=['GET'])
def decrypt():  

  # Format the potential passenger's name
  # The No-Fly list already been normalized to remove spaces and force lower case
  orig_name = request.args.get('name')
  name = ''.join(orig_name.split()).lower()

  # Compare our name to the unencrypted list
  if name in plaintext_nofly_list:
    message = "{} is on the no-fly list and CAN NOT BOARD!\n".format(orig_name)
  else:
    message = "{} is cleared to fly. Enjoy your flight!\n".format(orig_name)

  return message

if __name__ == '__main__':
    app.run(port=os.getenv('PORT', 8000))
