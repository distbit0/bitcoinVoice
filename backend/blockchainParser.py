def extractOpReturnText(output):
    import re, binascii
    script = str(output.script)
    opReturn = re.search("OP_RETURN ([^\s]+)", script)   
    try:
        return binascii.unhexlify(opReturn).decode("utf-8")
    except: return ""
    
    
def subtractFromDataBase(transaction):
    for txInput in transaction.inputs:
        index = txInput.transaction_index
        txid = txInput.transaction_hash
        db.remove("txid": txid, "index": index)
            
    
def addToDataBase(transaction, time):
    opReturns = {}
    txid = transaction.hash
    for no, output in enumerate(transaction.outputs):
        if output.is_return():
            opReturn = extractOpReturnText(output)
            if opReturn and len(transaction.outputs) => no + 1:
                valueBuddy = transaction.outputs[no+1]
                value = valueBuddy.satoshis
                opReturns.append({"opReturn": opReturn, "value": value, "index":no+1, "time": time, "txid": txid})
   for opReturn in opReturns:
        opReturn = opReturns[opReturn]
        db.addRow(opReturn)
    
    
def scan(): 
    # Instantiate the Blockchain by giving the path to the directory 
    # containing the .blk files created by bitcoind 
    import sys
    from blockchain_parser.blockchain import Blockchain
    blockchain = Blockchain(sys.argv[1])
    for block in blockchain.get_unordered_blocks():
        blockTime = block.header.timestamp
        for tx in block.transactions:
            addToDataBase(tx, blockTime)
            subtractFromDatabse(tx)     
