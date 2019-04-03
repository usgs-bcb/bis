def getWoRMSSearchURL(searchType,target):
    if searchType == "ExactName":
        return  "http://www.marinespecies.org/rest/AphiaRecordsByName/"+target+"?like=false&marine_only=false&offset=1"
    elif searchType == "FuzzyName":
        return  "http://www.marinespecies.org/rest/AphiaRecordsByName/"+target+"?like=true&marine_only=false&offset=1"
    elif searchType == "AphiaID":
        return "http://www.marinespecies.org/rest/AphiaRecordByAphiaID/"+str(target)
    elif searchType == "searchAphiaID":
        return "http://www.marinespecies.org/rest/AphiaIDByName/"+str(target)+"?marine_only=false"

def buildWoRMSTaxonomy(wormsData):
    taxonomy = []
    for taxRank in ["kingdom","phylum","class","order","family","genus"]:
        taxonomy.append({"rank":taxRank.title(),"name":wormsData[taxRank]})
    taxonomy.append({"rank":"Species","name":wormsData["valid_name"]})
    return taxonomy

def lookupWoRMS(nameString):
    import requests
    from datetime import datetime
    
    wormsResult = {}
    wormsResult["Processing Metadata"] = {}
    wormsResult["Processing Metadata"]["Date Processed"] = datetime.utcnow().isoformat()
    wormsResult["Processing Metadata"]["Summary Result"] = "Not Matched"

    wormsData = []
    aphiaIDs = []
    
    url_ExactMatch = getWoRMSSearchURL("ExactName",nameString)
    nameResults_exact = requests.get(url_ExactMatch)
    
    if nameResults_exact.status_code == 200:
        wormsDoc = nameResults_exact.json()[0]
        wormsDoc["taxonomy"] = buildWoRMSTaxonomy(wormsDoc)
        wormsResult["Processing Metadata"]["Search URL"] = url_ExactMatch
        wormsResult["Processing Metadata"]["Summary Result"] = "Exact Match"
        wormsData.append(wormsDoc)
        if wormsDoc["AphiaID"] not in aphiaIDs:
            aphiaIDs.append(wormsDoc["AphiaID"])
    else:
        url_FuzzyMatch = getWoRMSSearchURL("FuzzyName",nameString)
        wormsResult["Processing Metadata"]["Search URL"] = url_FuzzyMatch
        nameResults_fuzzy = requests.get(url_FuzzyMatch)
        if nameResults_fuzzy.status_code == 200:
            wormsDoc = nameResults_fuzzy.json()[0]
            wormsDoc["taxonomy"] = buildWoRMSTaxonomy(wormsDoc)
            wormsResult["Processing Metadata"]["Summary Result"] = "Fuzzy Match"
            wormsData.append(wormsDoc)
            if wormsDoc["AphiaID"] not in aphiaIDs:
                aphiaIDs.append(wormsDoc["AphiaID"])


    if len(wormsData) > 0 and "valid_AphiaID" in wormsData[0].keys():
        valid_AphiaID = wormsData[0]["valid_AphiaID"]
        while valid_AphiaID is not None:
            if valid_AphiaID not in aphiaIDs:
                url_AphiaID = getWoRMSSearchURL("AphiaID",valid_AphiaID)
                aphiaIDResults = requests.get(url_AphiaID)
                if aphiaIDResults.status_code == 200:
                    wormsDoc = aphiaIDResults.json()
                    wormsDoc["taxonomy"] = buildWoRMSTaxonomy(wormsDoc)
                    wormsResult["Processing Metadata"]["Search URL"] = url_AphiaID
                    wormsResult["Processing Metadata"]["Summary Result"] = "Followed Valid AphiaID"
                    wormsData.append(wormsDoc)
                    if wormsDoc["AphiaID"] not in aphiaIDs:
                        aphiaIDs.append(wormsDoc["AphiaID"])
                    if "valid_AphiaID" in wormsDoc.keys():
                        valid_AphiaID = wormsDoc["valid_AphiaID"]
                    else:
                        valid_AphiaID = None
                else:
                    valid_AphiaID = None
            else:
                valid_AphiaID = None

    if len(wormsData) > 0:
        wormsResult["wormsData"] = wormsData

    return (wormsResult)

