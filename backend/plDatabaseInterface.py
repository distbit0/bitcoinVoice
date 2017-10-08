# unspentDB
# Database functions for publicLabelOutput actions.

'''
createPLrecord - all columns.
deletePLrecord - txID and sequence#
searchPLrecords - publicLabel, start date, end date.
'''


import psycopg2
import sys

# connect to the postgres DB 

try:
    conn = psycopg2.connect("dbname='bitcoinVoice'  user='postgres' password='99' host='localhost' ")
    print("Connected to bitcoinVoice DB...")
except:
    print ("I am unable to connect to the database")
    print (sys.exc_info()[0])
    print (sys.exc_info())
    

def deleteAllPublicLabels(chainID):
    print("Hey! We are deleting the databse!")
    cursor = conn.cursor()
    cursor.execute('DELETE from "publicLabelOutput" where "chainID" = %s', (chainID,))
    conn.commit()

def getUnspentPublicLabelMaxHeight(chainID) :
    # return the maximum height of all the public labels
    cursor = conn.cursor()
    cursor.execute('SELECT max("plBlockHeightCreated") from "publicLabelOutput" where "chainID" = %s', (chainID,))
    
    # get the result set
    desc = cursor.description
    columnNames = [col[0] for col in desc]
    publicLabels = [dict(zip(columnNames, row))  
        for row in cursor.fetchall()]
    
    maxHeight = publicLabels[0]["max"]
    
    #print("maxHeight = " + str(maxHeight))
    if maxHeight : return maxHeight
    else : return 0
    
    
def getUnspentPublicLabels(chainID) :
    # return a list of transactions
    cursor = conn.cursor()
   
    cursor.execute('SELECT "txID", "txOutputSequence" from "publicLabelOutput" where "chainID" = %s and "unixTimeSpent" = 0',(chainID,))
    
    # get the result set
    desc = cursor.description
    columnNames = [col[0] for col in desc]
    publicLabels = [dict(zip(columnNames, row))  
        for row in cursor.fetchall()]

    
    return publicLabels
    
    
def setSpentTime(chainID, TxID, TxOutputSequence, Time):
    # update the unixTimeSpent for a publicLabelOutput record - given a TxID and sequence#    
    # NOTE - Currently silent if no record is found to delete.

    cursor = conn.cursor()

    cursor.execute('UPDATE unixTimeSpent = %s from "publicLabelOutput" where "chainID" = %s and "txID" = %s and "txOutputSequence" = %s', (TxID, TxOutputSequence, Time,))
    
    conn.commit()


def getBlockchainList():
    # return a list of the online blockchains config data
    cursor = conn.cursor()
   
    cursor.execute('SELECT "chainID", "chainName", "rpcport", "pathToBlockchain", "unitsCode" from "blockchain" where "online"=TRUE')
    
    # get the result set
    desc = cursor.description
    columnNames = [col[0] for col in desc]
    blockchainList = [dict(zip(columnNames, row))  
        for row in cursor.fetchall()]

    
    return blockchainList
    
    
    
def deletePLrecord(chainID, TxID, TxOutputSequence):
    # Deletes an publicLabelOutput record from the database - given a TxID and sequence#    
    # NOTE - Currently silent if no record is found to delete.

    cursor = conn.cursor()

    cursor.execute('DELETE from "publicLabelOutput" where "chainID" = %s and "txID" = %s and "txOutputSequence" = %s', (chainID, TxID, TxOutputSequence,))

    conn.commit()



def getFilteredPublicLabels(chainID, publicLabel, startDate, endDate):
    # returns a dictionary of unspent public label outputs given public label and a date range filters
    # Date range is in unixtime - seconds since midnight 1 Jan 1970. Calling routine to specify the INT date range.

    cursor = conn.cursor()
    print(startDate)
    print(endDate)
    if publicLabel :
        cursor.execute('SELECT * from "publicLabelOutput" where "chainID" = %s and "unixTimeSpent" = 0 and "publicLabel" like %s and "unixTimeCreated" >= %s and "unixTimeCreated" <= %s order by "txID", "txOutputSequence"', (chainID, publicLabel, float(startDate), float(endDate),))
    else: 
        cursor.execute('SELECT * from "publicLabelOutput" where "chainID" = %s and "unixTimeSpent" = 0 and "unixTimeCreated" >= %s and "unixTimeCreated" <= %s order by "txID", "txOutputSequence"', (chainID, float(startDate), float(endDate),))

    # get the result set
    desc = cursor.description
    columnNames = [col[0] for col in desc]
    publicLabels = [dict(zip(columnNames, row))  
        for row in cursor.fetchall()]
        
    return publicLabels



def createPLrecord(chainID, TxID, TxOutputSequence, publicLabel, amount, unixTime, blockHeight):
    # Creates a new database record publicLabelOutput
    # NOTE - performs no uniqueness checking - assumes the DB will handle that.

    cursor = conn.cursor()
    
    # Create a dictionary from the input params
    PLTxDict = {} # Placeholder dictionary
    
    # Assign the values to the dictionary
    PLTxDict["txID"]             = TxID    
    PLTxDict["txOutputSequence"] = TxOutputSequence    
    PLTxDict["publicLabel"]      = publicLabel    
    PLTxDict["amountInSatoshis"] = amount    
    PLTxDict["unixTimeCreated"]  = unixTime
    PLTxDict["plBlockHeightCreated"] = blockHeight
    PLTxDict["chainID"] = chainID
    

    # create a new DB record from the dictionary.
    return insertDict(cursor, "publicLabelOutput", PLTxDict)


def insertDict(curs, tableName, data):
    # Inserts a new record into tableName given a dictionary
                                                
    fields = data.keys()
    values = data.values()
    placeholder = "%s"
    fieldList = (', '.join('"' + item + '"' for item in fields))    #  ",".join(fields)
    placeholderList = ",".join([placeholder] * len(fields))

    query = 'insert into "' + tableName + '"(%s) values (%s)' % (fieldList, placeholderList)

    fullQuery = curs.mogrify(query, list(values))
    print(fullQuery)
    curs.execute(fullQuery)
    conn.commit()    



'''
# TESTING CODE

TxID               = "123126"
TxOutputSequence   = 2
publicLabel        = "small hands"
amount             = 0.5
unixTime           = 810


createPLrecord(TxID, TxOutputSequence, publicLabel, amount, unixTime)

pubLabList = searchPLrecords("sm%",3 , 900) # wildcard search in PL


print ("Before\n")
print (pubLabList)

input("Press Enter to continue...")

deletePLrecord(TxID, TxOutputSequence)

'''


'''
createPLrecord(TxID, TxOutputSequence, publicLabel, amount, unixTime)
'''

'''
pubLabList = searchPLrecords("sm%",3 , 900)
print ("After\n")
print (pubLabList)
'''


'''
if pubLabList:
    print ('\n\nPublic Label List: ', pubLabList[0]['TxID'])
'''


