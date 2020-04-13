#!/usr/bin/python
#Streaming 
import grpc
from concurrent import futures
import time

import devices_pb2
import devices_pb2_grpc

# open a gRPC channel
channel = grpc.insecure_channel('localhost:50051')

# create a stub (client)
stub = devices_pb2_grpc.Device_InformationStub(channel)

protomsg = devices_pb2.Info()
protomsg.name = "Arista"
protomsg.role = "Spine"
#protomsg.vlanlist.extend([100,200,400])
print("before being passed into grpc this is what it should look like")
print(protomsg)
response = stub.Network(protomsg)
print("After being returned into grpc this is what it should look like")
print(response)