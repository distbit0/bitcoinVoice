#############################################################################################
#
# Bitcoin Voice - Database interface   
#
############################################################################################## 

import psycopg2
import sys
import uuid
import datetime

# connect to the postgres DB 
try:
    conn = psycopg2.connect("dbname='bitcoinVoice'  user='postgres' password='99' host='localhost' ")
    print("Connected to bitcoinVoice DB...")
except:
    print ("I am unable to connect to the database")
    print (sys.exc_info()[0])
    print (sys.exc_info())

#################################################################    
def updateLatestCheckedBlockHeight(chainID, latest_block):
    # update the latestCheckedBlockHeight field to indicate the block has been checked for public label outputs
    
    #print('Updating latestCheckedBlockHeight to %s for chainID %s'%(latest_block, str(chainID),))    
    cursor = conn.cursor()
    cursor.execute('UPDATE "blockchain" SET "latestCheckedBlockHeight" = %s WHERE "chainID" = %s', (latest_block, chainID,))
    conn.commit()

    
#################################################################    
def deleteRecentData(chainID, recentBestBlock) :
    # delete recent data from blockInfo and publicLabelsOutput
    print('Deleting data processed after block height %s'%(recentBestBlock))
    # delete recent data because it could have been scanned from an orphaned branch
    cursor = conn.cursor()
    # delete ALL blockInfo rows for recent blocks on this chain
    cursor.execute('DELETE from "blockInfo" where "chainID" = %s and "blockHeight" >= %s', (chainID, recentBestBlock, )) 
    # delete ALL publicLabelOutputs for recent blocks on this chain
    cursor.execute('DELETE from "publicLabelOutput" where "chainID" = %s and "plBlockHeightCreated" >= %s', (chainID, recentBestBlock ,))        
    conn.commit()

    
#################################################################    
def blockInfoCheckZeroErrors(chainID, blockhash) :
    # delete any data about recent blocks
    # return the number of blockInfo rows with zero errors
    
    cursor = conn.cursor()
        
    # return the number of blockInfo rows with zero errors
    cursor.execute('SELECT "blockInfoID" from "blockInfo" where "chainID" = %s and "blockhash" = %s and "countOutputsWithErrors" = 0', (chainID, blockhash))
    
    return cursor.rowcount

#################################################################    
def getLatestCheckedBlockHeight(chainID) :
    # return the maximum height of all the public labels
    cursor = conn.cursor()

    cursor.execute('SELECT max("latestCheckedBlockHeight") from "blockchain" where "chainID" = %s', (chainID,))
    
    # get the result set
    desc = cursor.description
    columnNames = [col[0] for col in desc]
    publicLabels = [dict(zip(columnNames, row))  
        for row in cursor.fetchall()]
    

    maxHeight = publicLabels[0]["max"]
    
    #print("maxHeight = " + str(maxHeight))
    if maxHeight : return maxHeight
    else : return 0


#################################################################    
def deleteAllPublicLabels(chainID):
    print('Hey! We are deleting the publicLabelOutputs for chainID %s'%(str(chainID),))
    cursor = conn.cursor()
    cursor.execute('DELETE from "publicLabelOutput" where "chainID" = %s'%(str(chainID),))
    conn.commit()


#################################################################
# NOT USED DEPRECATED FOR getLatestCheckedBlockHeight()
def getUnspentPublicLabelMaxHeight(chainID) :
    # return the maximum height of all the public labels
    cursor = conn.cursor()
    print('SELECT max("plBlockHeightCreated") from "publicLabelOutput" where "chainID" = %s'%(chainID,))
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
    
#################################################################    
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

    cursor.execute('UPDATE "publicLabelOutput" SET "unixTimeSpent" = %s WHERE "chainID" = %s and "txID" = %s and "txOutputSequence" = %s', (Time, chainID, TxID, TxOutputSequence,))
    
    conn.commit()

#################################################################
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
    
    
#################################################################    
def deletePLrecord(chainID, TxID, TxOutputSequence):
    # Logically 'deletes' an publicLabelOutput record from the database - given a TxID and sequence#    
    # NOTE - Currently silent if no record is found to delete.

    cursor = conn.cursor()

    '''
    FIX THIS TO FIND THE RECORD THEN WRITE THE spent TIME TO THE RECORD. i.e. DON'T delete it from the DB.
    
    '''
    cursor.execute('DELETE from "publicLabelOutput" where "chainID" = %s and "txID" = %s and "txOutputSequence" = %s', (chainID, TxID, TxOutputSequence,))

    conn.commit()


#################################################################
def getFilteredPublicLabels(chainID, publicLabel, startDate, endDate):
    # returns a dictionary of UNSPENT public label outputs given public label and a date range filters
    # Date range is in unixtime - seconds since midnight 1 Jan 1970. Calling routine to specify the INT date range.

    cursor = conn.cursor()
    
    #print(datetime.datetime.fromtimestamp(float(startDate)).strftime('%Y-%m-%d %H:%M:%S'))
    #print(datetime.datetime.fromtimestamp(float(endDate)).strftime('%Y-%m-%d %H:%M:%S'))
    
    if publicLabel :
        # insert wild cards 
        publicLabel = "%" + publicLabel + "%"
        cursor.execute('SELECT * from "publicLabelOutput" where "chainID" = %s and "unixTimeSpent" = 0 and "publicLabel" ilike %s and "unixTimeCreated" >= %s and "unixTimeCreated" <= %s order by "txID", "txOutputSequence"', (chainID, publicLabel, float(startDate), float(endDate),))
        
        
    else: # there is no filter on the public label
        cursor.execute('SELECT * from "publicLabelOutput" where "chainID" = %s and "unixTimeSpent" = 0 and "unixTimeCreated" >= %s and "unixTimeCreated" <= %s order by "txID", "txOutputSequence"', (chainID, float(startDate), float(endDate),))

    # get the result set
    desc = cursor.description
    columnNames = [col[0] for col in desc]
    publicLabels = [dict(zip(columnNames, row))  
        for row in cursor.fetchall()]
        
    return publicLabels

#################################################################
def insertOrUpdateBlockInfoRecord(chainID, blockhash, unixTimeLastScan, countOutputsWithPublicLabels, countOutputsWithSpentPublicLabels, countOutputsWithErrors, txid, blockHeight) :
    # Inserts or updates the blockInfo data using the results from a scan
    
    cursor = conn.cursor()
    cursor.execute('UPDATE "blockInfo" SET "lastErrorTxID" = %s, "unixTimeLastScan" = %s, "countOutputsWithPublicLabels" = %s, "countOutputsWithSpentPublicLabels" = %s, "countOutputsWithErrors" = %s, "blockHeight" = %s WHERE "chainID" = %s and "blockhash" = %s',
         (txid, unixTimeLastScan, countOutputsWithPublicLabels, countOutputsWithSpentPublicLabels, countOutputsWithErrors, blockHeight, chainID, blockhash))
    
    
    # try the update first
    conn.commit()   
   
    # if the update didn't work then try insert 
    if cursor.rowcount == 0 :
        
        # Create a dictionary from the input params
        rec = {} # Placeholder dictionary
        
        # Assign the values to the dictionary
        rec["blockInfoID"]                          = str(uuid.uuid4())
        rec["lastErrorTxID"]                        = txid
        rec["blockhash"]                            = blockhash
        rec["blockHeight"]                          = blockHeight
        rec["unixTimeLastScan"]                     = unixTimeLastScan    
        rec["countOutputsWithPublicLabels"]         = countOutputsWithPublicLabels
        rec["countOutputsWithSpentPublicLabels"]    = countOutputsWithSpentPublicLabels
        rec["countOutputsWithErrors"]               = countOutputsWithErrors
        rec["chainID"]                              = chainID
        

        # create a new DB record from the dictionary.
        insertDict(cursor, "blockInfo", rec)
 
#################################################################
def createPLrecord(chainID, TxID, TxOutputSequence, publicLabel, amount, unixTime, blockHeight):
    # Creates a new database record publicLabelOutput
    # NOTE - performs no uniqueness checking - assumes the DB will handle that.

    cursor = conn.cursor()
    
    cursor.execute('UPDATE "publicLabelOutput" SET "publicLabel" = %s, "plBlockHeightCreated" = %s, "amountInSatoshis" = %s, "unixTimeCreated" = %s, "unixTimeSpent" = 0 WHERE "chainID" = %s and "txID" = %s and "txOutputSequence" = %s',
         (publicLabel, blockHeight, amount, unixTime, chainID, TxID, TxOutputSequence))
    
    
    # try the update first
    conn.commit()   
   
   # if the update returns 0 then it probably doesn't exist so insert
    if cursor.rowcount == 0 :
    
        # Create a dictionary from the input params
        rec = {} # Placeholder dictionary
        
        # Assign the values to the dictionary
        rec["txID"]                 = TxID    
        rec["txOutputSequence"]     = TxOutputSequence    
        rec["publicLabel"]          = publicLabel    
        rec["amountInSatoshis"]     = amount    
        rec["unixTimeCreated"]      = unixTime
        rec["unixTimeCreated"]      = 0
        rec["plBlockHeightCreated"] = blockHeight
        rec["chainID"]              = chainID
        

        # create a new DB record from the dictionary.
        result = insertDict(cursor, "publicLabelOutput", rec)

#################################################################
def insertDict(curs, tableName, data):
    # Inserts a new record into tableName given a dictionary
                                                
    fields = data.keys()
    values = data.values()
    placeholder = "%s"
    fieldList = (', '.join('"' + item + '"' for item in fields))    #  ",".join(fields)
    placeholderList = ",".join([placeholder] * len(fields))

    query = 'insert into "' + tableName + '"(%s) values (%s)' % (fieldList, placeholderList)

    fullQuery = curs.mogrify(query, list(values))
    #print(fullQuery)
    curs.execute(fullQuery)
    conn.commit()    
    
    return curs.rowcount

#################################################################
def spendPLrecord(chainID, TxID, outputSequence, unixtimeSpent):
    # Sets the unixTimeSpend value for the specified PL record
    

    cursor = conn.cursor()
    
    cursor.execute('UPDATE "publicLabelOutput" SET "unixTimeSpent" = %s WHERE "chainID" = %s and "txID" = %s and "txOutputSequence" = %s', (float(unixtimeSpent), chainID, TxID, outputSequence,))
    '''
    cursor.execute('SELECT * from "publicLabelOutput" where "chainID" = %s and "unixTimeSpent" = 0 and "publicLabel" like %s and "unixTimeCreated" >= %s and "unixTimeCreated" <= %s order by "txID", "txOutputSequence"', (chainID, publicLabel, float(startDate), float(endDate),))
    '''
    
    # get the result set
    desc = cursor.description
    columnNames = [col[0] for col in desc]
    publicLabels = [dict(zip(columnNames, row))  
        for row in cursor.fetchall()]
        
    return publicLabels



'''
def spendPLrecord(chainID, TxID, outputSequence):
    """ update PL record's unixtimeSpent  """
    sql = """ UPDATE publicLabelOutput
                SET unixTimeSpent = %s
                WHERE chainID = %s AND txID = %s and txOutputSequence = %s"""
    conn = None
    updated_rows = 0
    try:
        

        # execute the UPDATE  statement
        cur.execute(sql, (spentTimeValue, chainID, TxID, outputSequence))  #MIGHT NEED TO float() some of these parameters
        # get the number of updated rows
        updated_rows = cur.rowcount
        # Commit the changes to the database
        conn.commit()
        # Close communication with the PostgreSQL database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
'''




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



