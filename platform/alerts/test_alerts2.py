#!/usr/bin/env python

from APNSWrapper import APNSNotificationWrapper, APNSNotification
import binascii

#deviceId = '1c8cf15acb17f8362322ccff0452417dcd3f6b538193099e0347efb84e8a4a4f' # kevin
deviceId = 'f02e7b4c384e32404645443203dd0b71750e54fe13b5d0a8a434a12a0f5e7a25' # bart
deviceId = '8b78c702f8c8d5e02c925146d07c28f615283bc862b226343f013b5f8765ba5a' # travis
deviceId = '01c386bff1c7b576629c3e4e3b101181d3acdfdb0947ba4ac5e513fb59775fc7' # mike

# create wrapper
wrapper = APNSNotificationWrapper('apns-dev.pem', True)

# create message
message = APNSNotification()
message.token(binascii.unhexlify(deviceId))
message.alert('TEST')
message.badge(5)

# add message to tuple and send it to APNS server
wrapper.append(message)
wrapper.notify()

