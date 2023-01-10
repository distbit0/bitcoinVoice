import datetime, sys, time, traceback
from bitcoinrpc.authproxy import AuthServiceProxy


def initRPCConnection(rpcport, rpcconnect, rpcuser, rpcpassword):
    #############################################################################################
    # Initialize rpc connection
    #############################################################################################
    rpc_connection = None
    # rpc connection
    #print("\n######################################################################################")
    #print("Initiating RPC using " + "http://%s:%s@%s:%s"%(rpcuser, rpcpassword, rpcconnect, rpcport))

    rpc_connection = AuthServiceProxy("http://%s:%s@%s:%s"%(rpcuser, rpcpassword, rpcconnect, rpcport))

    return rpc_connection

rpcconnect="127.0.0.1"
# rpc_user and rpc_password
rpcuser="bitcoinvoice"
rpcpassword="Ql2c1ElsR3nyuI56yBX75KeORn-mz0F4jBwLVxOzQVE="
rpcport="8330"
rpc_connection = initRPCConnection(rpcport, rpcconnect, rpcuser, rpcpassword)
tx = rpc_connection.getrawtransaction("2d05f0c9c3e1c226e63b5fac240137687544cf631cd616fd34fd188fc9020866")
tx = rpc_connection.decoderawtransaction(tx)
print(tx)