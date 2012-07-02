#!/usr/bin/env python

import os, sys, pymongo, json, struct, ssl, binascii
from socket import socket

base = os.path.dirname(os.path.abspath(__file__))

IPHONE_APN_PUSH_CERT_DEV  = os.path.join(base, 'apns-dev.pem')
IPHONE_APN_PUSH_CERT_PROD = os.path.join(base, 'apns-prod.pem')

host_name = 'gateway.sandbox.push.apple.com'
#host_name = 'gateway.push.apple.com'

#deviceId = '1c8cf15acb17f8362322ccff0452417dcd3f6b538193099e0347efb84e8a4a4f' # kevin
#deviceId = 'f02e7b4c384e32404645443203dd0b71750e54fe13b5d0a8a434a12a0f5e7a25' # bart
deviceId = '8b78c702f8c8d5e02c925146d07c28f615283bc862b226343f013b5f8765ba5a' # travis
deviceId = '9d943f189085639bd87bac6c9dd2b89f237bee1e232041d4057f7a422f23deeb' #landon
deviceId = 'df687e03345604f6b02a4c32bc7d5220ddd5f832c270645e06f22cc26f66516a' # Kevin

# Build payload
content = {
    'aps': {
        'alert': "Testing",
        # 'sound': 'default',
    }
}
s_content = json.dumps(content, separators=(',',':'))

# Format actual notification
fmt = "!cH32sH%ds" % len(s_content)
command = '\x00'

payload = struct.pack(fmt, command, 32, binascii.unhexlify(deviceId), \
                      len(s_content), s_content)

s = socket()
c = ssl.wrap_socket(s, 
                    ssl_version=ssl.PROTOCOL_SSLv3, 
                    certfile=IPHONE_APN_PUSH_CERT_PROD)
c.connect((host_name, 2195))
c.write(payload)
c.close()

