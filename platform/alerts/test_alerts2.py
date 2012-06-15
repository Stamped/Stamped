#!/usr/bin/env python

from APNSWrapper import APNSNotificationWrapper, APNSNotification
import binascii

#apnstoken = '1c8cf15acb17f8362322ccff0452417dcd3f6b538193099e0347efb84e8a4a4f' # kevin
#apnstoken = 'f02e7b4c384e32404645443203dd0b71750e54fe13b5d0a8a434a12a0f5e7a25' # bart
#apnstoken = '8b78c702f8c8d5e02c925146d07c28f615283bc862b226343f013b5f8765ba5a' # travis
apnstoken = '01c386bff1c7b576629c3e4e3b101181d3acdfdb0947ba4ac5e513fb59775fc7' # mike
#apnstoken = '48e3496a9fdadcc8ce8fe99020bb461a72bd0e20e1a8ee0878494133f8c23d4c' #landon
#apnstoken = '9d943f189085639bd87bac6c9dd2b89f237bee1e232041d4057f7a422f23deeb' #landon

# create wrapper
#wrapper = APNSNotificationWrapper('apns-dev.pem', True)
wrapper = APNSNotificationWrapper('apns-ether.pem', True)

# create message
message = APNSNotification()
message.token(binascii.unhexlify(apnstoken))
message.alert('TEST')
message.badge(5)

# add message to tuple and send it to APNS server
wrapper.append(message)
wrapper.notify()

