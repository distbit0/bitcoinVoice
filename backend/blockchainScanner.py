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
import datetime, sys, time
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

def extractOpReturnText(script):
    #############################################################################################
    #
    # Bitcoin Voice - extract data from OP_RETURN script
    #
    #############################################################################################

    import re, binascii

    try:
        # speed up search since this line is faster than the regex search in extractOpReturn
        if not "OP_RETURN" in script : return ""

        # searches script for OP_RETURN and returns data
        opReturn = re.search("OP_RETURN ([^\s]+).([^\s]+)", script).groups()
        # could be more formats to handle

        opReturn = binascii.unhexlify(opReturn[1]).decode("utf-8")
        opReturn = opReturn.replace("\0", "")
        return opReturn
    except: return ""



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
        rpc_connection = None

    print("######################################################################################")
    print("")

    return rpc_connection


def updateSpentPLRows(chainID):
    #############################################################################################
    #
    # Bitcoin Voice - Scan the bitcoinVoice DB Top Public Labels and set spent date
    #
    #############################################################################################
    print("\n### Updating spent public labels ...")

    # loop every bitcoinVoicePLRecord row and remove spent votes
    unspentPublicLabels = []
    unspentPublicLabels = getUnspentPublicLabels(chainID)
    for tx in unspentPublicLabels :
        #print(tx)

        # test if this output is spent - gettxout is designed to return unspent only when txindex=1 is in bitcoin.conf
        isUnspentOut = rpc_connection.gettxout(tx["txID"], tx["txOutputSequence"])

        # the output has just been spent
        if not isUnspentOut:
            print("########## Updating spent public label ..." + str(tx["txID"]) + " " + str(tx["txOutputSequence"]))
            # since gettxout only returns unspent data its hard to know the block when the public label was spent at this time
            setSpentTime(chainID, tx["txID"], tx["txOutputSequence"], time.time(), None, None)
        #else :
        #    print("UnSpent.")


def addUnspentPLRows(chainID):
    #############################################################################################
    #
    # Bitcoin Voice - Scan the blockchain for Top Public Labels and create unspent bitcoinVoicePLRecords
    #
    #############################################################################################

    print("\n### Adding unspent public labels ...")

    # get last block via best block
    best_block_hash = rpc_connection.getbestblockhash()
    best_block = rpc_connection.getblock(best_block_hash)
    last_block = best_block["height"]
    #last_block = 1201012 # this block is one in testnet that we know has a public label


    # define first block height from maximum height already stored
    first_block = getLatestCheckedBlockHeight(chainID) + 1;
    #first_block = 1201011  # first sample tx with pair
    #first_block = 0        # uncomment to start again from empty table

    # rescan the most recent blocks
    #"If we only need to sync less than 10 blocks, sync the lasy ten anyway incase a re-org happened"
    if last_block - first_block <= rescanRecentBlocks: first_block = last_block - rescanRecentBlocks

    print("Verifying range from block " + str(first_block) + " to " + str(last_block))

     # don't need to start scanning too early
    if first_block > last_block :
        print("Perhaps the blockchain needs more synching to get up to date.")
        return

    # delete recent data
    deleteRecentData(chainID, best_block["height"] - rescanRecentBlocks)

    print("Scanning from block " + str(first_block) + " to " + str(last_block))
    try:

            # batch support : print timestamps of blocks 0 to 99 in 2 RPC round-trips:
            commands = [[ "getblockhash", height] for height in range(first_block, last_block)]
            block_hashes = rpc_connection.batch_(commands)

            # load the public labels for spent test
            unspentPublicLabels = []
            unspentPublicLabels = getUnspentPublicLabels(chainID)

            print("Scanning block data for public label outputs...")
            # loop through block hashes in range
            for h in block_hashes:
                #print(h)

                # test if block exists in the blockInfo DB table
                # if it exists and countOutputsWithErrors = 0 then skip the blockscan
                #if blockInfoCheckZeroErrors(chainID, h) > 0 : continue

                # block stats
                countOutputsWithPublicLabels = 0
                countOutputsWithSpentPublicLabels = 0
                countOutputsWithErrors = 0

                # load block
                block = rpc_connection.getblock(h)
                #print ("Block # : " + str(block["height"]))

                # for each transaction in a block scan the outputs with public labels
                for txid in block["tx"]:
                    #print(txid)

                    # extract the raw transaction
                    try:
                        # capture error but continue when invalid txs are found :/
                        rawTx = rpc_connection.getrawtransaction(txid)
                        tx = rpc_connection.decoderawtransaction(rawTx)

                    except JSONRPCException : # common error "No information available about transaction"
                        countOutputsWithErrors += 1
                        print(sys.exc_info())
                        break
                    except :
                        countOutputsWithErrors += 1
                        print(sys.exc_info())
                        break

                    # public labels are formed in pairs so to exist there would at least be 2 outputs
                    if len(tx["vout"]) < 2 : continue


                    # loop through outputs in a block
                    for n, out in enumerate(tx["vout"]):
                        #print(str(n))
                        if out["value"] != 0 : continue

                        script = out["scriptPubKey"]["asm"]
                        #print(script)

                        # test if there are any public labels
                        opReturn = extractOpReturnText(script)

                        # if there is an opReturn then extract the value buddy from the following output
                        if n + 1 <= len(tx["vout"])-1 and opReturn:
                            countOutputsWithPublicLabels += 1

                            valueBuddyOutput = tx["vout"][n + 1]
                            value = valueBuddyOutput["value"] *100000000

                            print("########## Adding unspent public label: " + datetime.datetime.fromtimestamp(block["time"]).strftime('%Y-%m-%d %H:%M:%S') + "\nPublic Label: " + str(opReturn.rstrip()) + " Value: " + str(value) + " Height: " + str(block["height"]))

                            createPLrecord(chainID, tx["txid"], n + 1, opReturn, value, block["time"], block["height"])

                            # test if the output is spent
                            isUnspentOut = rpc_connection.gettxout(txid, n + 1)

                            # if the output is spent then keep count
                            if isUnspentOut:
                                pass
                            else:
                                countOutputsWithSpentPublicLabels += 1

                            # refresh public labels
                            unspentPublicLabels = getUnspentPublicLabels(chainID)
                    # end for loop of outputs in transactions

                    # search here for spend txs that relate to local public labels and set the plBlockHeightSpent field
                    for n, txinput in enumerate(tx["vin"]):
                        #print (txinput)
                        if not "coinbase" in list(txinput.keys()) :
                            for pltx in unspentPublicLabels :
                                #print(txinput)
                                if pltx["txID"] == txinput["txid"] and pltx["txOutputSequence"] == txinput["vout"] :
                                    # the transaction tx["txID"], tx["txOutputSequence"] spends a public label
                                    setSpentTime(chainID, pltx["txID"], pltx["txOutputSequence"], time.time(), block["height"], txid)
                                    print("########## Updating spent public label in block " + str(block["height"]) + " : " + pltx["publicLabel"])
                    # end for loop of inputs

                # end for loop of transactions in block

                # for each block save the results from the block scan
                if countOutputsWithErrors > 0 :
                    insertOrUpdateBlockInfoRecord(chainID, h, datetime.datetime.now().timestamp(), countOutputsWithPublicLabels, countOutputsWithSpentPublicLabels, countOutputsWithErrors, txid, block["height"])
                else :
                    # completed scan of blocks in range without errors so now mark as done by updating latestCheckedBlockHeight
                    if block["height"] < best_block["height"] - rescanRecentBlocks :
                        updateLatestCheckedBlockHeight(chainID, block["height"])
                    # insert a blockInfo record so that future scans can skip this block (or comment out to speed up current scan)
                    # insertOrUpdateBlockInfoRecord(chainID, h, datetime.datetime.now().timestamp(), countOutputsWithPublicLabels, countOutputsWithSpentPublicLabels, countOutputsWithErrors, txid, block["height"])

                # end for loop of blocks in range


    except :
                print ("Block # : " + str(block["height"]))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(str(sys.exc_info()) + "\n\nOn line: " + str(exc_tb.tb_lineno))
                sys.exit()

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

            # chainID as startup parameter to scan only a single chain, leave blank to scan all online chains
            if len(sys.argv) == 1 or int(blockchain["chainID"]) == int(sys.argv[1]) :
                print("Starting scan of blockchain " + str(blockchain["chainName"]))

                # initialize the rpc connection for the blockchain
                rpcport=blockchain["rpcport"]
                rpc_connection = initRPCConnection(rpcport, rpcconnect, rpcuser, rpcpassword)

                if rpc_connection :
                    print("Connected to blockchain " + str(blockchain["chainName"]) + " on port " + str(rpcport))
                    print("")

                    # update the bitcoinVoice DB data set for the blockchain
                    addUnspentPLRows(blockchain["chainID"])
                    updateSpentPLRows(blockchain["chainID"])

                print("Completed scan of blockchain " + str(blockchain["chainName"]) + " on port " + str(rpcport))
                print("")

        time.sleep(300)



