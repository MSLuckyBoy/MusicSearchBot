import requests
import json

import base64
import hashlib
import hmac
import os
import sys
import time

'''
with open("config.json") as f:
    Config = json.load(f)

def search(url):
    data = {
        'url': f'{url}',
        'api_token': Config['api_token']
    }

    result = requests.post('https://api.audd.io/', data=data)

    return result.text
'''


access_key = "3a529d0cb27721880774d99355ec488e"
access_secret = "benLAMqidbHs5C59dqfI1e4WYYsUSlfWIPNxF7G9"
requrl = "http://identify-eu-west-1.acrcloud.com/v1/identify"

http_method = "POST"
http_uri = "/v1/identify"

data_type = "audio"
signature_version = "1"
timestamp = time.time()

string_to_sign = http_method + "\n" + http_uri + "\n" + access_key + "\n" + data_type + "\n" + signature_version + "\n" + str(timestamp)

sign = base64.b64encode(
    hmac.new(access_secret.encode('ascii'),
    string_to_sign.encode('ascii'),
    digestmod=hashlib.sha1).digest()
).decode('ascii')

f = open(sys.argv[0], "rb")
sample_bytes = os.path.getsize(sys.argv[0])


def search(url):
    muz = requests.get(url, allow_redirects=True)

    files = [
        ('sample', ('2.ogg', muz.content, 'audio/ogg'))
    ]

    data = {'access_key': access_key,
        'sample_bytes': sample_bytes,
        'timestamp': str(timestamp),
        'signature': sign,
        'data_type': data_type,
        "signature_version": signature_version
    }

    r = requests.post(requrl, files=files, data=data)
    r.encoding = "utf-8"

    parsed = json.loads(r.text)

    print(json.dumps(parsed, indent=4, sort_keys=True))

    return None

