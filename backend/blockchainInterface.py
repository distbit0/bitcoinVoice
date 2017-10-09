#############################################################################################
#
# Bitcoin Voice - Web API connecting bitcoinVoice DB
#
#############################################################################################

from plDatabaseInterface import *   
 
# returns a list of aggregated public labels that are unspent and calculates the subtotals  
def getPublicLabelAggregates(chainID, startPos, endPos, startDate, endDate, searchTerm):
    publicLabels = {}
    output = []
    
    # get a list of filtered unspent public labels
    records = getFilteredPublicLabels(chainID, searchTerm, startDate, endDate)

    # loop each sub public label into the aggregate list
    for record in records:
        if record["publicLabel"] in publicLabels:
            publicLabels[record["publicLabel"]] += record["amountInSatoshis"]/100000000
        else:
            publicLabels[record["publicLabel"]] = record["amountInSatoshis"]/100000000
    i = 0
    
    # sort the aggregated list
    for key, value in sorted(publicLabels.items(), key=lambda i: i[1], reverse=True):
        i+= 1
        output.append({"rank": i, "label": key, "utxo": value})
    output = output[endPos:startPos]
    return output

    
# returns a list of non-aggregated public labels that are unspent so aggregate layer can use drill down
def getPublicLabels(chainID):
    publicLabels = {}
    output = []
    # get a list of filtered unspent public labels
    records = getFilteredPublicLabels(chainID, searchTerm, startDate, endDate)
    
    # sort the non-aggregated list
    for key, value in sorted(records.items(), key=lambda i: i[1], reverse=True):
        i+= 1
        output.append({"rank": i, "label": key, "utxo": value})
    output = output[endPos:startPos]
    return output

