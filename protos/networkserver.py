#!/usr/bin/python

import grpc
from concurrent import futures
import time

import devices_pb2
import devices_pb2_grpc

import devices_pb2_grpc
#class Device_InformationServicer(devices_pb2_grpc.Device_InformationServicer):
class Device_InformationServicer(devices_pb2_grpc.Device_InformationServicer):
    def Network(self, request, context):
        response = devices_pb2.Info()
        response.name = (request.name)
        response.role = (request.role)
        #response.rolelist = (request.rolelist)
        if response.role == 'Leaf':
            return response 
        else:
            protomsg = devices_pb2.Info()
            protomsg.name = "Arista"
            protomsg.role = "Something other than a Leaf"
            return protomsg

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

devices_pb2_grpc.add_Device_InformationServicer_to_server(Device_InformationServicer(), server)

print('Starting server. Listening on port 50051.')
server.add_insecure_port('[::]:50051')
server.start()

try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)