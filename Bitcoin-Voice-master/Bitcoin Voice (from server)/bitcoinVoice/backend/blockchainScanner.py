#############################################################################################
#
# Bitcoin Voice - Perform a scan of online blockchains for public labels
#
#############################################################################################
#
# STARTUP:
# python3 blockchainScanner.py <chainID>
#
# <chainID> is optional and selects only a single chain, leave blank to scan all online chains
#
#############################################################################################
from plDatabaseInterface import *
import datetime, sys, time, traceback
from bitcoinrpc.authproxy import AuthServiceProxy

def logError(error):
    #############################################################################################
    # Log errors to a file
    #############################################################################################
    with open("scannerErrors.txt", "a+") as errorFile:
        errorFile.write("\n\n" + str(error) + "\n\n")


def extractOpReturnText(script):
    #############################################################################################
    # Extract data from OP_RETURN script
    #############################################################################################
    import re, binascii

    try:
        # speed up search since this line is faster than the regex search in extractOpReturn
        if not "OP_RETURN" in script : return ""

        # searches script for OP_RETURN and returns data
        opReturns = script.split(" ")
        # could be more formats to handle
        if len(opReturns) > 2:
            potentialPrefix = opReturns[1]
            potentialOPCode = opReturns[2]
            if potentialOPCode[0:3] == "OP_":
                opReturn = binascii.unhexlify(potentialPrefix).decode("utf-8").replace("\0", "")
            else:
                opReturn = binascii.unhexlify(potentialOPCode).decode("utf-8").replace("\0", "")
        else:
            opReturn = binascii.unhexlify(opReturns[1]).decode("utf-8").replace("\0", "")
        return opReturn
    except: return ""


def initRPCConnection(rpcport, rpcconnect, rpcuser, rpcpassword):
    #############################################################################################
    # Initialize rpc connection
    #############################################################################################
    rpc_connection = None
    # rpc connection
    print("Initiating RPC using " + "http://%s:%s@%s:%s"%(rpcuser, rpcpassword, rpcconnect, rpcport))

    rpc_connection = AuthServiceProxy("http://%s:%s@%s:%s"%(rpcuser, rpcpassword, rpcconnect, rpcport))
    try: print(rpc_connection.getinfo())
    except:
        logError("###############INIT RPC ERROR:###############\n" + str(sys.exc_info()) + "\n" +  "".join(traceback.format_tb(sys.exc_info()[2]))) #log error to file

    return rpc_connection

def reattemptFailedScans(chainID):
    print("\n\nRe-attempting failed scans on chain: " + str(chainID) + ":")
    failedScans = getFailedScanRecords(chainID) #gets list of blocks/txs that didn't successfully scan from db table "failedScans"
    for failedScan in failedScans:
        try:
            if failedScan["objectType"] == "block": #if the failed object is a block, rescan it
                scanBlock(failedScan["objectID"], chainID, rescan=True) #use re-scan = True so that it doesn't mark this block as lastCheckedBlock in db
            if failedScan["objectType"] == "transaction": #if it is a tx, rescan it
                block = rpc_connection.getblock(failedScan["blockHash"])
                scanTransaction(failedScan["objectID"], chainID, block)
        except:
            #log that this RESCAN failed! to log file :/ (usually not a great sign)
            print("FAILED rescan of " + failedScan["objectType"] + " " + failedScan["objectID"])
            logError("RETRY:\n" + failedScan["objectType"] + " exception: \n" + failedScan["objectType"] + "Hash: " + str(failedScan["objectID"]) + "\n" + str(sys.exc_info()) + "\n" +  "".join(traceback.format_tb(sys.exc_info()[2]))) #log error to file
        else:
            print("SUCCEEDED rescan of " + failedScan["objectType"] + " " + failedScan["objectID"])
            deleteFailedScan(chainID, failedScan["objectID"], failedScan["objectType"], failedScan["blockHash"]) #remove record from db sfter successful rescan

def updateSpentPLRows(chainID):
    #############################################################################################
    # Scan the bitcoinVoice DB Top Public Labels and set spent date
    #############################################################################################
    print("\n\nUpdating spent public labels for chain: " + str(chainID) + ":")

    # loop every bitcoinVoicePLRecord row and remove spent votes
    unspentPublicLabels = getUnspentPublicLabels(chainID)
    for tx in unspentPublicLabels :
        # test if this output is spent - gettxout is designed to return unspent only when txindex=1 is in bitcoin.conf
        isUnspentOut = rpc_connection.gettxout(tx["txID"], tx["txOutputSequence"])

        # since gettxout only returns unspent data its hard to know the block when the public label was spent at this time
        if not isUnspentOut:
            print("Updating spent public label in tx: " + str(tx["txID"]) + " output#: " + str(tx["txOutputSequence"]))
            setSpentTime(chainID, tx["txID"], tx["txOutputSequence"], time.time(), None, None)


def scanTransaction(txid, chainID, block):
    # extract the raw transaction, this sometimes causes an error if the node can't find the tx :/
    rawTx = rpc_connection.getrawtransaction(txid)
    tx = rpc_connection.decoderawtransaction(rawTx)

    #public labels are formed in pairs so to exist there would at least be 2 outputs
    if len(tx["vout"]) < 2 : return

    # loop through outputs in a tx
    for n, out in enumerate(tx["vout"]):
        if out["value"] != 0: continue #only want OP_RETURN outs and they can't contain coins
        if not len(tx["vout"]) > n + 1: continue

        script = out["scriptPubKey"]["asm"]
        # test if there are any public labels
        opReturn = extractOpReturnText(script)

        # if there is an opReturn then extract the value buddy from the following output
        if opReturn:
            valueBuddyOutput = tx["vout"][n + 1]
            value = valueBuddyOutput["value"]*100000000
            createPLrecord(chainID, tx["txid"], n + 1, opReturn, value, block["time"], block["height"]) #this MIGHT error out but VERY UNLIKELY


def scanBlock(blockHash, chainID, rescan=False):
    #load block
    block = rpc_connection.getblock(blockHash)
    # for each transaction in a block, scan the outputs
    for txid in block["tx"]:
        try:
            scanTransaction(txid, chainID, block)
        except:
            addFailedScanRecord(chainID, txid, "transaction", blockHash) #log to failedScans table for re-try later
            logError("Transaction exception: \nTransaction Hash: " + str(txid) + "\n" + str(sys.exc_info()) + "\n" +  "".join(traceback.format_tb(sys.exc_info()[2]))) #log error to file
            #print("Transaction exception: \nTransaction Hash: " + str(txid))
    if not rescan: #if this function is being called to retry past block, we don't want to set last scanned block to far in the past
        updateLatestCheckedBlockHeight(chainID, block["height"]) #mark this block as the most last block in db

def addUnspentPLRows(chainID):
    #############################################################################################
    # Bitcoin Voice - Scan the blockchain for Top Public Labels and create unspent bitcoinVoicePLRecord
    #############################################################################################
    print("\nAdding unspent public labels for chain " + str(chainID) + ":")
    # get last block via best block
    best_block_hash = rpc_connection.getbestblockhash()
    best_block = rpc_connection.getblock(best_block_hash)
    last_block = best_block["height"]
    # define first block height from maximum height already stored
    first_block = getLatestCheckedBlockHeight(chainID) + 1;
    #print("Best block on chain " + str(chainID) + " is " + str(last_block) + " while the last checked block is " + str(first_block))
    #"If we only need to sync less than 10 blocks, sync the last ten anyway incase a re-org happened"
    if last_block - first_block <= rescanRecentBlocks: first_block = last_block - rescanRecentBlocks

    # don't need to start scanning too early if the blocks aren't downloaded yet!
    if first_block > last_block :
        print("Node not synced to last checked block")
        return

    deleteRecentData(chainID, first_block) # delete records since lastcheckedblockheight in case of a rescan or reorg onchain (^^)

    print("Scanning from block " + str(first_block) + " to " + str(last_block) + " for public label outputs.\n")

    # batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
    commands = [[ "getblockhash", height] for height in range(first_block, last_block + 1)]
    block_hashes = rpc_connection.batch_(commands)

    # loop through block hashes in range
    for blockHash in block_hashes:
        print("Scanning block: " + blockHash)
        try:
            scanBlock(blockHash, chainID)
        except:
            addFailedScanRecord(chainID, blockHash, "block")
            logError("Block exception: \nBlock Hash: " + str(blockHash) + "\n" + str(sys.exc_info()) + "\n" +  "".join(traceback.format_tb(sys.exc_info()[2]))) #log error to file
            #print("Block exception: \nBlock Hash: " + str(blockHash))

#############################################################################################
#
# Bitcoin Voice - Top Public Labels refresh DB
#
#############################################################################################


print("Started Bitcoin Voice data builder...")

# specify the recent blocks to rescan
rescanRecentBlocks = 10

# setup bitcoin.conf connections
rpcconnect="127.0.0.1"
# rpc_user and rpc_password
rpcuser="bitcoinvoice"
rpcpassword="Ql2c1ElsR3nyuI56yBX75KeORn-mz0F4jBwLVxOzQVE="

# loop the defined blockchains and process the ones that are marked online
blockchainList = getBlockchainList()
while True:
        for blockchain in blockchainList :
            if len(sys.argv) == 1 or int(blockchain["chainID"]) == int(sys.argv[1]): #Check if chainID was supplied as command line arg
                print("\n\n\n\nStarting scan of blockchain " + str(blockchain["chainName"]) + ":")
                print("############################################################################################################################################")
                try:
                    # initialize the rpc connection for the blockchain
                    rpcport=blockchain["rpcport"]
                    rpc_connection = initRPCConnection(rpcport, rpcconnect, rpcuser, rpcpassword) #connects to full node

                    if rpc_connection :
                        print("Connected to blockchain " + str(blockchain["chainName"]) + " on port " + str(rpcport) + "\n")

                        # update the bitcoinVoice DB data set for the blockchain
                        addUnspentPLRows(blockchain["chainID"]) #scans from last scanned block for any new OP_RETURN+value output containing txs
                        updateSpentPLRows(blockchain["chainID"]) #sets txs that have been spent as "spent" in db so that they don't contribute to scores
                        reattemptFailedScans(blockchain["chainID"]) #re attempts a scan on all blocks/txs that encounted errors in their scan
                except:
                    logError(str(sys.exc_info()) + "\n" +  "".join(traceback.format_tb(sys.exc_info()[2]))) #log error to file

                print("\n\nCompleted scan of blockchain " + str(blockchain["chainName"]) + " on port " + str(rpcport))

        time.sleep(300) #wait a bit (5 mins)
