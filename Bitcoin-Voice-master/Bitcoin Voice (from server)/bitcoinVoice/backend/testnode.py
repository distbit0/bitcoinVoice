from bitcoinrpc.authproxy import AuthServiceProxy

def initRPCConnection(rpcport, rpcconnect, rpcuser, rpcpassword):
    #############################################################################################
    # Initialize rpc connection
    #############################################################################################
    rpc_connection = None
    # rpc connection
    print("Initiating RPC using " + "http://%s:%s@%s:%s"%(rpcuser, rpcpassword, rpcconnect, rpcport))
    print("\n\n")
    rpc_connection = AuthServiceProxy("http://%s:%s@%s:%s"%(rpcuser, rpcpassword, rpcconnect, rpcport))
    print(rpc_connection.getinfo())
    print("\n\n")

    return rpc_connection
    


rpcconnect="127.0.0.1"
# rpc_user and rpc_password
rpcuser="bitcoinvoice"
rpcpassword="Ql2c1ElsR3nyuI56yBX75KeORn-mz0F4jBwLVxOzQVE="

rpc_connection = initRPCConnection(8330, rpcconnect, rpcuser, rpcpassword)
rpc_connection = initRPCConnection(8331, rpcconnect, rpcuser, rpcpassword)
rpc_connection = initRPCConnection(8332, rpcconnect, rpcuser, rpcpassword)
rpc_connection = initRPCConnection(8333, rpcconnect, rpcuser, rpcpassword)
