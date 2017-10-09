#############################################################################################
#
# Bitcoin Voice - Perform a scan of online blockchains for public labels   
#
############################################################################################## 

from plDatabaseInterface import *
import datetime, sys
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import logging

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
        print("extractOpReturnText error: " + sys.exc_info())
        return ""
    
    
def initRPCConnection(rpcport, rpcconnect, rpcuser, rpcpassword):
    #############################################################################################
    #
    # Bitcoin Voice - Initialize rpc connection  
    #
    #############################################################################################
    
    # UNCOMMENT HERE TO DEBUG RPC IN stdout
    #logging.basicConfig()
    #logging.getLogger("BitcoinRPC").setLevel(logging.DEBUG)
    
    # rpc connection 
    print("")
    print("######################################################################################")
    print("Initiating RPC using " + "http://%s:%s@%s:%s"%(rpcuser, rpcpassword, rpcconnect, rpcport))
    
    rpc_connection = AuthServiceProxy("http://%s:%s@%s:%s"%(rpcuser, rpcpassword, rpcconnect, rpcport))
    try : print(rpc_connection.getinfo()) 
    except : 
        print("ERROR: Connection failed.")
        print(sys.exc_info())
        return 
    
    print("######################################################################################")
    print("")    
    return rpc_connection


def updateSpentPLRows(chainID):
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
            print("########## Updating spent public label ..." + str(tx["txID"]) + " " + str(tx["txOutputSequence"]))
            block = rpc_connection.getblock(isUnspentOut["bestblock"])
            setSpentTime(tx["txID"], tx["txOutputSequence"], block["time"]) 
                   


def addUnspentPLRows(chainID):
    #############################################################################################
    #
    # Bitcoin Voice - Top Public Labels create unspent bitcoinVoicePLRecords
    #
    #############################################################################################
    print("Adding unspent public labels ...")
        
    # get last block via best block
    best_block_hash = rpc_connection.getbestblockhash()
    best_block = rpc_connection.getblock(best_block_hash)
    last_block = best_block["height"] - 6
    # last_block = 1201012 # this block is one in testnet that we know has a public label
    
    
    # define first block height from maximum height already stored
    first_block = getLatestCheckedBlockHeight(chainID) + 1;
    #first_block = 1201011  # first sample tx with pair
    #first_block = 0        # uncomment to start again from empty table
    
 
    # reset table
    if first_block < 1060000: 
        deleteAllPublicLabels(chainID)
        first_block = 1060000 # this block is around Dec-2016
        
     # don't need to start scanning too early
    if first_block > last_block : 
        print("Perhaps the blockchain needs more synching to get up to date.")
        last_block = first_block   
        return 
        
        
    print("Scanning from block " + str(first_block) + " to " + str(last_block))

    # batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
    commands = [[ "getblockhash", height] for height in range(first_block, last_block)]
    block_hashes = rpc_connection.batch_(commands)

    print("Scanning block data for public label outputs...")
    # loop through block hashes in range
    for h in block_hashes:
        #print(h)    
        
        # block stats
        countOutputsWithPublicLabels = 0
        countOutputsWithSpentPublicLabels = 0
        countOutputsWithErrors = 0
            
        block = rpc_connection.getblock(h)
        # for each transaction in a block scan the outputs with public labels 
        for txid in block["tx"]:
            

            # extract the raw transaction        
            try:
                # capture error but continue when invalid txs are found :/
                rawTx = rpc_connection.getrawtransaction(txid)      
                tx = rpc_connection.decoderawtransaction(rawTx)
                
            except JSONRPCException : # common error "No information available about transaction"    
                countOutputsWithErrors += 1
                #print(sys.exc_info()) 
                break            
            except :
                countOutputsWithErrors += 1
                print(sys.exc_info())
                break
            
            # loop through outputs in a block        
            for n, out in enumerate(tx["vout"]):
                            
                # test if there are any public labels 
                if out["scriptPubKey"]["type"] == "publiclabel" :
                    script = out["scriptPubKey"]["asm"]
                    #print(script)
                    opReturn = extractOpReturnText(script)
                    
                    # if there is an opReturn then extract the value from the following output
                    if n + 1 <= len(tx["vout"]) and opReturn:      
                        countOutputsWithPublicLabels += 1              
                        
                        # test if the output is spent
                        isUnspentOut = rpc_connection.gettxout(txid, n + 1)

                        # if the output is unspent then add to the database                
                        if isUnspentOut:
                            valueBuddyOutput = tx["vout"][n + 1]
                            value = valueBuddyOutput["value"] *100000000
                            
                            print("########## Adding unspent public label: " + datetime.datetime.fromtimestamp(block["time"]).strftime('%Y-%m-%d %H:%M:%S') + "Public Label: " + str(opReturn.rstrip()) + " Value: " + str(value) + " Height: " + str(block["height"]))

                            createPLrecord(chainID, tx["txid"], n + 1, opReturn, value, block["time"], block["height"])
                            
                        else:
                            countOutputsWithSpentPublicLabels += 1
                            
            # end for loop of outputs in transactions
        # end for loop of transactions in block    
        
        # for each block save the results from the block scan
        if countOutputsWithErrors > 0 :
            insertOrUpdateBlockInfoRecord(chainID, h, datetime.datetime.now().timestamp(), countOutputsWithPublicLabels, countOutputsWithSpentPublicLabels, countOutputsWithErrors, txid)
        else :
            # completed scan of blocks in range without errors so now mark as done by updating latestCheckedBlockHeight
            updateLatestCheckedBlockHeight(chainID, block["height"])
                
        # end for loop of blocks in range        
                
    return
    

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
    
    if rpc_connection :
        print("Connected to blockchain " + str(blockchain["chainName"]) + " on port " + str(rpcport))
        print("")

        # update the bitcoinVoice DB data set for the blockchain
        updateSpentPLRows(blockchain["chainID"])
        addUnspentPLRows(blockchain["chainID"])





