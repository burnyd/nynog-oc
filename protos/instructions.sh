#create a protobuf for devices proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. devices.proto
