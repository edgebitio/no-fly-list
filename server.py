import os
import json
from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import base64
import boto3

app = Flask(__name__)

def decrypt_list(file_contents):

  session = boto3.session.Session()
  kms = session.client('kms')

  binary_data = base64.b64decode(file_contents)
  meta = kms.decrypt(CiphertextBlob=binary_data)
  plaintext = meta[u'Plaintext']

  return plaintext.decode().split(',')

def fetchS3():

  s3 = boto3.resource('s3')

  # This object has a public access policy
  obj = s3.Object('no-fly-list', 'no-fly-encrypted.txt')
  return obj.get()['Body'].read().decode('utf-8')

@app.route('/')
def index():
  return jsonify("https://edgebit.com/enclaver/docs/0.x/guide-app/")

@app.route('/enclave/passenger', methods=['GET'])
def decrypt():

  # Fetch the encrypted No-Fly list stored on S3
  encrypted_base64_contents = fetchS3()

  # Format the potential passenger's name
  # The No-Fly list already been normalized to remove spaces and force lower case
  orig_name = request.args.get('name')
  name = ''.join(orig_name.split()).lower()

  # Decrypt the No-Fly list
  # Enclaver will attach the cryptographic attestation of this enclave to the request
  # The KMS key has an access policy that explictly allows this attestation access to the key
  plaintext_nofly_list = decrypt_list(encrypted_base64_contents)

  # Compare our name to the unencrypted list
  if name in plaintext_nofly_list:
    message = "{} is on the no-fly list and CAN NOT BOARD!\n".format(orig_name)
  else:
    message = "{} is cleared to fly. Enjoy your flight!\n".format(orig_name)

  return message

if __name__ == '__main__':
    app.run(port=os.getenv('PORT', 8000))
