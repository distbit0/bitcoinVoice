import bchrpc_pb2
import grpc
channel = grpc.insecure_channel('bchd.greyh.at:8335')
stub =  bchrpc_pb2_grpc.pb_bchrpc(channel)
stub
