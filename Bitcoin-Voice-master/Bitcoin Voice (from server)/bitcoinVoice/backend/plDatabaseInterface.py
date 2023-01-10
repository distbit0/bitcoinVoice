#############################################################################################
#
# Bitcoin Voice - Database interface
#
##############################################################################################

import psycopg2
import sys
import uuid
# connect to the postgres DB
try:
    conn = psycopg2.connect("dbname='bitcoinVoice' user='postgres' port=5433 password='abcd1234' host='localhost' ")
    print("Connected to bitcoinVoice DB...")
except:
    print ("Error connecting to the database.")
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
    # delete ALL publicLabelOutputs for recent blocks on this chain
    cursor.execute('DELETE from "publicLabelOutput" where "chainID" = %s and "plBlockHeightCreated" >= %s', (chainID, recentBestBlock ,))
    conn.commit()


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
def getUnspentPublicLabels(chainID) :
    # return a list of transactions
    cursor = conn.cursor()

    cursor.execute('SELECT "txID", "txOutputSequence", "publicLabel" from "publicLabelOutput" where "chainID" = %s and "unixTimeSpent" = 0',(chainID,))

    # get the result set
    desc = cursor.description
    columnNames = [col[0] for col in desc]
    publicLabels = [dict(zip(columnNames, row))
        for row in cursor.fetchall()]

    return publicLabels


def setSpentTime(chainID, TxID, TxOutputSequence, Time, Height, txIDSpent):
    # update the unixTimeSpent for a publicLabelOutput record - given a TxID and sequence#
    # NOTE - Currently silent if no record is found to delete.

    cursor = conn.cursor()

    cursor.execute('UPDATE "publicLabelOutput" SET "unixTimeSpent" = %s, "plBlockHeightSpent" = %s, "txIDSpent" = %s WHERE "chainID" = %s and "txID" = %s and "txOutputSequence" = %s', (Time, Height, txIDSpent, chainID, TxID, TxOutputSequence,))

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
def getFilteredPublicLabels(chainID, publicLabel, startDate, endDate, exactMatchOnly=False):
    # returns a dictionary of UNSPENT & SPENT public label outputs given public label and a date range filters
    # Date range is in unixtime - seconds since midnight 1 Jan 1970. Calling routine to specify the INT date range.

    cursor = conn.cursor()



    if publicLabel :

        # insert wild cards
        if not exactMatchOnly:
            publicLabel = "%" + publicLabel + "%"

        cursor.execute('SELECT * from "publicLabelOutput" where "chainID" = %s ' + ' and "publicLabel" ilike %s and "unixTimeCreated" >= %s and "unixTimeCreated" <= %s order by "txID", "txOutputSequence"', (chainID, publicLabel, float(startDate), float(endDate),))
    else: # there is no filter on the public label
        cursor.execute('SELECT * from "publicLabelOutput" where "chainID" = %s ' + ' and "unixTimeCreated" >= %s and "unixTimeCreated" <= %s order by "txID", "txOutputSequence"', (chainID, float(startDate), float(endDate),))

    # get the result set
    desc = cursor.description
    columnNames = [col[0] for col in desc]
    publicLabels = [dict(zip(columnNames, row))
        for row in cursor.fetchall()]

    return publicLabels


def addFailedScanRecord(chainID, objectID, objectType, blockHash=None) :
    # Logs id of failed scan of block or tx so that it can be retried in the future
    print("Adding failed scan of " + objectType + " " + objectID)
    cursor = conn.cursor()
    cursor.execute('SELECT "chainID", "objectID", "objectType", "blockHash" from "failedScans" where "objectID" = %s', (objectID,))


    # try the update first
    conn.commit()

    # if the update didn't work then try insert
    if cursor.rowcount == 0 :

        # Create a dictionary from the input params
        rec = {} # Placeholder dictionary

        # Assign the values to the dictionary
        rec["chainID"]                              = chainID
        rec["objectID"]                             = objectID
        rec["objectType"]                           = objectType
        rec["blockHash"]                            = blockHash


        # create a new DB record from the dictionary.
        insertDict(cursor, "failedScans", rec)


def getFailedScanRecords(chainID):
    # return a list of all failed txids and block hashes

    cursor = conn.cursor()

    cursor.execute('SELECT "chainID", "objectID", "objectType", "blockHash" from "failedScans" where "chainID" = %s', (chainID,))

    # get the result set
    desc = cursor.description
    columnNames = [col[0] for col in desc]
    failedScans = [dict(zip(columnNames, row))
        for row in cursor.fetchall()]


    return failedScans

def deleteFailedScan(chainID, objectID, objectType, blockHash=None):
    # Logically 'deletes' a failed scan record from the db, given its id, blockID and objectType
    # NOTE - Currently silent if no record is found to delete.

    cursor = conn.cursor()
    #print("deleting failed scan on chain " + str(chainID) + " and of " + objectType + " " + objectID)
    #print("block hash: " + str(blockHash))
    if blockHash != None:
        cursor.execute('DELETE from "failedScans" where "chainID" = %s and "objectID" = %s and "objectType" = %s and "blockHash" = %s', (chainID, objectID, objectType, blockHash,))
    else: #for some reason the db doesn't delete block rows if we search for blockHash=None so we just don't include it at all
        cursor.execute('DELETE from "failedScans" where "chainID" = %s and "objectID" = %s and "objectType" = %s', (chainID, objectID, objectType,))
    conn.commit()
    #print("the amount of rows deleted was: " + str(cursor.rowcount))

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
        rec["plBlockHeightCreated"] = blockHeight
        rec["chainID"]              = chainID


        # create a new DB record from the dictionary.
        insertDict(cursor, "publicLabelOutput", rec)

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

    # get the result set
    desc = cursor.description
    columnNames = [col[0] for col in desc]
    publicLabels = [dict(zip(columnNames, row))
        for row in cursor.fetchall()]

    return publicLabels