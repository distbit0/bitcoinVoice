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

    # get a list of filtered unaggregated unspent public labels
    records = getFilteredPublicLabels(chainID, searchTerm, startDate, endDate)

    # loop each sub public label into the aggregate list
    for record in records:
        if record["unixTimeSpent"] == 0:
            if record["publicLabel"] in publicLabels:
                publicLabels[record["publicLabel"]] += record["amountInSatoshis"]/100000000
            else:
                publicLabels[record["publicLabel"]] = record["amountInSatoshis"]/100000000
        else:
            if not record["publicLabel"] in publicLabels:
                publicLabels[record["publicLabel"]] = 0

    # sort the aggregated list
    i = 0
    for key, value in sorted(publicLabels.items(), key=lambda i: i[1], reverse=True):
        i+= 1
        output.append({"rank": i, "label": key, "amt": value})
    return output[startPos:endPos]



# returns a list of non-aggregated public labels that are unspent so aggregate layer can use drill down on a label
def getPublicLabelOutputs(chainID, startDate, endDate, startPos, endPos, publicLabel, onlyUnspent):
    utxos = []
    publicLabels = {}

    # get a list of filtered unaggregated unspent public labels
    records = getFilteredPublicLabels(chainID, publicLabel, startDate, endDate, True)
    for record in records:
        if onlyUnspent == 1 and record["unixTimeSpent"] != 0:
            continue
        publicLabels[record["txID"]] = record

    # sort the list by unixTimeCreated
    for key, value in sorted(publicLabels.items(), key=lambda i: i[1]["unixTimeCreated"], reverse=True):
        utxos.append({"txid": value["txID"],
                        "amt": value["amountInSatoshis"]/100000000,
                        "plblockHeightCreated": value["plBlockHeightCreated"],
                        "txOutputSequence": value["txOutputSequence"],
                        "unixTimeCreated": value["unixTimeCreated"],
                        "unixTimeSpent": value["unixTimeSpent"],
                        "txIDSpent": value["txIDSpent"],
                        "plBlockHeightSpent": value["plBlockHeightSpent"],
                        "publicLabel": value["publicLabel"]})

    return utxos[startPos:endPos]

