import sys
from blockchain_parser.blockchain import Blockchain

def initDataBase():
    pass
    
    
def extractOpReturnText(output):
    import re, binascii
    script = str(output.script)
    opReturn = re.search("OP_RETURN ([^\s]+)", script)   
    try:
        return binascii.unhexlify(opReturn).decode("utf-8")
    except: return ""
    
    
def get
    
    
def subtractFromDataBase(transaction):
    for no, txInput in enumerate(transaction.inputs):
        #If input in databse:
            
    
def addToDataBase(transaction):
    opReturns = {}
    txid = transaction.hash
    for no, output in enumerate(transaction.outputs):
        if output.is_return():
            opReturn = extractOpReturnText(output)
            if opReturn and len(transaction.outputs) > no + 1:
                valueBuddy = transaction.outputs[no+1]
                value = valueBuddy.satoshis/100000000
                opReturns[opReturn] =  opReturns[opReturn] = ["value": value, "index":no]
    #for opReturn in opReturns:
        #db.addRow(txid, opReturn, opReturns[opReturn]["value"], opReturns[opReturn]["index"])
    
    
# Instantiate the Blockchain by giving the path to the directory 
# containing the .blk files created by bitcoind
blockchain = Blockchain(sys.argv[1])
with open("opReturns.txt", "a") as opReturnFile:
    for block in blockchain.get_unordered_blocks():
        for tx in block.transactions:
            addToDataBase(tx)
            subtractFromDatabse(tx)     
