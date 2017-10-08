    from plDatabaseInterface import *
import datetime, sys
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException


def extractOpReturnText(script):   
    #############################################################################################
    #
    # Bitcoin Voice - extract data from OP_RETURN script  
    #
    #############################################################################################

    import re, binascii 
    
    # searches script for OP_RETURN and returns data
    opReturn = re.search("OP_RETURN ([^\s]+).([^\s]+)", script).groups()
    # could be more formats to handle
    
    try:
    
        opReturn = binascii.unhexlify(opReturn[1]).decode("utf-8")
        opReturn = opReturn.replace("\0", "");
        return opReturn
    except:   
        print(sys.exc_info())
        return ""
    
    
def initRPCConnection(rpcport, rpcconnect, rpcuser, rpcpassword):
    #############################################################################################
    #
    # Bitcoin Voice - Initialize rpc connection  
    #
    #############################################################################################
    
    # rpc connection 
    rpc_connection = AuthServiceProxy("http://%s:%s@%s:%s"%(rpcuser, rpcpassword, rpcconnect, rpcport))
    return rpc_connection


def updateSpentPLRows(rpc_connection, chainID):
    #############################################################################################
    #
    # Bitcoin Voice - Top Public Labels set spent bitcoinVoicePLRecords  
    #
    #############################################################################################
    print("Updating spent public labels ...")
  
    # loop every bitcoinVoicePLRecord row and remove spent votes
    unspentPublicLabels = []
    unspentPublicLabels = getUnspentPublicLabels(chainID)
    for tx in unspentPublicLabels :
        
        # test if the output is spent
        isUnspentOut = rpc_connection.gettxout(tx["txID"], tx["txOutputSequence"])

        # the output has just been spent                 
        if isUnspentOut == "":
            print("Updating spent public label ..." + str(tx["txID"]) + " " + str(tx["txOutputSequence"]))
            block = rpc_connection.getblock(isUnspentOut["bestblock"])
            setSpentTime(tx["txID"], tx["txOutputSequence"], block["time"]) 
                   


def addUnspentPLRows(rpc_connection, chainID):
    #############################################################################################
    #
    # Bitcoin Voice - Top Public Labels create unspent bitcoinVoicePLRecords
    #
    #############################################################################################
    print("Adding unspent public labels ...")
    
    # define first block height from maximum height already stored
    first_block = getUnspentPublicLabelMaxHeight(chainID) + 1;
    #first_block = 1201011  # first sample tx with pair
    #first_block = 0        # uncomment to start again from empty table
    
    # reset table
    if first_block < 1060000: 
        deleteAllPublicLabels()
        first_block = 1060000 # this block is around Dec-2016
        
    # get last block via best block
    best_block_hash = rpc_connection.getbestblockhash()
    best_block = rpc_connection.getblock(best_block_hash)
    last_block = best_block["height"] - 6
    #last_block = 1201012 # this block is one in testnet that we know has a public label
    
    print("Scanning from block " + str(first_block) + " to " + str(last_block))

    # batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
    commands = [[ "getblockhash", height] for height in range(first_block, last_block)]
    block_hashes = rpc_connection.batch_(commands)

    print("Getting block data...")

    # loop through block hashes
    for h in block_hashes:
        #print(h)    
        # for each tx in the block scan the outputs
        block = rpc_connection.getblock(h)
        for txid in block["tx"]:

            # extract the raw transaction        
            try:
                rawTx = rpc_connection.getrawtransaction(txid) #error, we are finidng lots fo invalid txs :/
                tx = rpc_connection.decoderawtransaction(rawTx)
            except JSONRPCException :                  
                continue            
            except :
                print(sys.exc_info())
                continue
            
            # loop through outputs         
            for n, out in enumerate(tx["vout"]):
                            
                # test if there are any public labels 
                if out["scriptPubKey"]["type"] == "publiclabel" :
                    script = out["scriptPubKey"]["asm"]
                    #print(script)
                    opReturn = extractOpReturnText(script)
                    
                    # if there is an opReturn then extract the value from the following output
                    if n + 1 <= len(tx["vout"]) and opReturn:                    
                        # test if the output is spent
                        isUnspentOut = rpc_connection.gettxout(txid, n + 1)

                        # if the output is unspent then add to the database                
                        if isUnspentOut:
                            valueBuddyOutput = tx["vout"][n + 1]
                            value = valueBuddyOutput["value"] *100000000
                            
                            print("########## AFTER ADDD = Date: " + datetime.datetime.fromtimestamp(block["time"]).strftime('%Y-%m-%d %H:%M:%S') + "Public Label: " + str(opReturn) + " Value: " + str(value))

                            createPLrecord(chainID, tx["txid"], n + 1, opReturn, value, block["time"], block["height"])
                            


#############################################################################################
#
# Bitcoin Voice - Top Public Labels refresh DB
#
#############################################################################################

print("Connecting to bitcoin rpc ...")

# setup bitcoin.conf connections
rpcconnect="127.0.0.1"
# rpc_user and rpc_password 
rpcuser="Ulysseys"
rpcpassword="abc123123"

# loop the defined blockchains and process the ones that are marked online
blockchainList = getBlockchainList()
for blockchain in blockchainList :
    # initialize the rpc connection for the blockchain
    rpcport=blockchain["rpcport"]
    rpc_connection = initRPCConnection(rpcport, rpcconnect, rpcuser, rpcpassword)
    print("Connected to blockchain " + str(blockchain["chainName"]) + " on port " + str(rpcport))

    # update the bitcoinVoice DB data set for the blockchain
    updateSpentPLRows(rpc_connection, blockchain["chainID"])
    addUnspentPLRows(rpc_connection, blockchain["chainID"])




