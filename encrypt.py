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

def push_S3(envelope):

  s3 = boto3.resource('s3')
  object = s3.Object('no-fly-list', 'no-fly-envelope.txt')

  object.put(
      Body=(bytes(json.dumps(envelope).encode('UTF-8')))
  )

def encrypt_envelope(list):

  # Get a KMS client
  client = boto3.client("kms")

  # Generate a new data key
  response = client.generate_data_key(KeyId="mrk-b3152356da604a7dac485a0a272957c7", KeySpec="AES_256")

  # The response includes both plaintext and encrypted versions of the data key
  plain_data_key = base64.b64encode(response["Plaintext"])
  encrypted_data_key = base64.b64encode(response["CiphertextBlob"])

  # Use the plaintext key to encrypt our data, and then throw it away
  f = Fernet(plain_data_key)
  crypted = f.encrypt(bytes(list, 'utf-8'))

  envelope = {}
  envelope["data-key-ciphertext-base64"] = encrypted_data_key.decode()
  envelope["aes-ciphertext-base64"] = crypted.decode()

  return envelope

@app.route('/')
def index():
  return jsonify("https://edgebit.com/enclaver/docs/0.x/guide-app/")

@app.route('/enclave/encrypt', methods=['POST'])
def encrypt():  

  # Read the list
  plaintext_list = request.form["list"]

  # Encrypt an envelope
  encrypted_envelope = encrypt_envelope(plaintext_list)

  # Upload it to S3
  push_S3(encrypted_envelope)

  return encrypted_envelope

if __name__ == '__main__':
    app.run(port=os.getenv('PORT', 8000))
