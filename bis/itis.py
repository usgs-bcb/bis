def getITISSearchURL(searchstr,fuzzy=False,validAccepted=True):
    fuzzyLevel = "~0.8"
    
    # Default to using name without indicator as the search term
    itisTerm = "nameWOInd"
    
    # "var." and "ssp." indicate that the string has population and variation indicators and should use the WInd service
    if searchstr.find("var.") > 0 or searchstr.find("ssp.") > 0 or searchstr.find(" x ") > 0:
        itisTerm = "nameWInd"
    
    try:
        int(searchstr)
        itisTerm = "tsn"
    except:
        pass
    
    # Put the search term together with the scientific name value including the escape character sequence that ITIS needs in the name criteria
    itisSearchURL = "http://services.itis.gov/?wt=json&rows=10&q="+itisTerm+":"+searchstr.replace(" ","\%20")

    # Add the specified fuzzy search level if asked for
    if fuzzy:
        itisSearchURL = itisSearchURL+fuzzyLevel

    # "valid" and "accepted" usage values will further constrain the search and handle cases where the search returns more than one possible record on name
    if validAccepted:
        itisSearchURL = itisSearchURL+"%20AND%20(usage:accepted%20OR%20usage:valid)"

    return itisSearchURL

def packageITISJSON(itisDoc):
    from datetime import datetime
    itisData = {}
    itisData["cacheDate"] = datetime.utcnow().isoformat()
    
    if type(itisDoc) is not int:
        # Get rid of parts of the ITIS doc that we don't want/need to cache
        primaryKeysToPop = ["_version_","credibilityRating","expert","geographicDivision","hierarchicalSort","hierarchyTSN","jurisdiction","publication","rankID","otherSource","taxonAuthor","comment"]

        for key in primaryKeysToPop:
            itisDoc.pop(key,None)

        # Make a clean structure of the taconomic hierarchy
        itisDoc["taxonomy"] = []
        for rank in itisDoc['hierarchySoFarWRanks'][0][itisDoc['hierarchySoFarWRanks'][0].find(':$')+2:-1].split("$"):
            thisRankName = {}
            thisRankName["rank"] = rank.split(":")[0]
            thisRankName["name"] = rank.split(":")[1]
            itisDoc["taxonomy"].append(thisRankName)
        itisDoc.pop("hierarchySoFarWRanks",None)
        
        # Make a clean, usable list of the hierarchy so far for display or listing
        itisDoc["hierarchy"] = itisDoc["hierarchySoFar"][0].split(":")[1][1:-1].split("$")
        itisDoc.pop("hierarchySoFar",None)

        # Make a clean structure of common names
        if "vernacular" in itisDoc:
            itisDoc["commonnames"] = []
            for commonName in itisDoc['vernacular']:
                thisCommonName = {}
                thisCommonName["name"] = commonName.split('$')[1]
                thisCommonName["language"] = commonName.split('$')[2]
                itisDoc["commonnames"].append(thisCommonName)
            itisDoc.pop("vernacular",None)
        
        # Add the new ITIS doc to the ITIS data structure and return 
        itisData.update(itisDoc)

    return itisData

def checkITISSolr(scientificname):
    import requests
    from datetime import datetime
    
    # Set up itisResult structure to return and prep the processingMetadata, set a default for Summary Result to Not Matched
    itisResult = {}
    itisResult["processingMetadata"] = {}
    itisResult["processingMetadata"]["Date Processed"] = datetime.utcnow().isoformat()
    itisResult["processingMetadata"]["Summary Result"] = "Not Matched"
    itisResult["processingMetadata"]["Detailed Results"] = []

    # Set up the primary search method for an exact match on scientific name    
    url_exactMatch = getITISSearchURL(scientificname,False,False)
    
    # We have to try the main search queries because the ITIS service does not return an elegant error
    try:
        r_exactMatch = requests.get(url_exactMatch).json()
    except:
        itisResult["processingMetadata"]["Detailed Results"].append({"Hard Fail Query":url_exactMatch})
        itisResult["processingMetadata"]["Summary Result"] = "Hard Fail Query"
        return itisResult
        
    if r_exactMatch["response"]["numFound"] == 0:
        
        itisResult["processingMetadata"]["Detailed Results"].append({"Exact Match Fail":url_exactMatch})
        
        # if we didn't get anything with an exact name match, run the sequence using fuzziness level
        url_fuzzyMatch = getITISSearchURL(scientificname,True,False)
        
        try:
            r_fuzzyMatch = requests.get(url_fuzzyMatch).json()
        except:
            itisResult["processingMetadata"]["Detailed Results"].append({"Hard Fail Query":url_fuzzyMatch})
            itisResult["processingMetadata"]["Summary Result"] = "Hard Fail Query"
            return itisResult
            
        if r_fuzzyMatch["response"]["numFound"] == 0:
            # If we still get no results then provide the specific detailed result
            itisResult["processingMetadata"]["Detailed Results"].append({"Fuzzy Match Fail":url_fuzzyMatch})
            return itisResult
            
        elif r_fuzzyMatch["response"]["numFound"] > 0:
            # If we got one or more results with a fuzzy match, we will just use the first result
            itisResult["itisData"] = []
    
            # We need to check to see if the discovered ITIS record is accepted for use. If not, we need to follow the accepted TSN in that document
            if r_fuzzyMatch["response"]["docs"][0]["usage"] in ["invalid","not accepted"]:
                url_tsnSearch = getITISSearchURL(r_fuzzyMatch["response"]["docs"][0]["acceptedTSN"][0],False,False)
                r_tsnSearch = requests.get(url_tsnSearch).json()
                itisResult["itisData"].append(packageITISJSON(r_tsnSearch["response"]["docs"][0]))
                itisResult["processingMetadata"]["Summary Result"] = "Followed Accepted TSN"
                itisResult["processingMetadata"]["Detailed Results"].append({"TSN Search":url_tsnSearch})
            else:
                itisResult["processingMetadata"]["Summary Result"] = "Fuzzy Match"
    
            # Whether or not we needed to follow an accepted TSN, we will also include the ITIS record that was the point of discovery
            itisResult["processingMetadata"]["Detailed Results"].append({"Fuzzy Match":url_fuzzyMatch})
            itisResult["itisData"].append(packageITISJSON(r_fuzzyMatch["response"]["docs"][0]))

    elif r_exactMatch["response"]["numFound"] == 1:
    # If we found only one record with the exact match query, we treat that as a useful point of discovery

        itisResult["itisData"] = []

        # We need to check to see if the discovered ITIS record is accepted for use. If not, we need to follow the accepted TSN in that document
        if r_exactMatch["response"]["docs"][0]["usage"] in ["invalid","not accepted"]:
            url_tsnSearch = getITISSearchURL(r_exactMatch["response"]["docs"][0]["acceptedTSN"][0],False,False)
            r_tsnSearch = requests.get(url_tsnSearch).json()
            itisResult["itisData"].append(packageITISJSON(r_tsnSearch["response"]["docs"][0]))
            itisResult["processingMetadata"]["Summary Result"] = "Followed Accepted TSN"
            itisResult["processingMetadata"]["Detailed Results"].append({"TSN Search":url_tsnSearch})
        else:
            itisResult["processingMetadata"]["Summary Result"] = "Exact Match"

        # Whether or not we needed to follow an accepted TSN, we will also include the ITIS record that was the point of discovery
        itisResult["processingMetadata"]["Detailed Results"].append({"Exact Match":url_exactMatch})
        itisResult["itisData"].append(packageITISJSON(r_exactMatch["response"]["docs"][0]))

    elif r_exactMatch["response"]["numFound"] > 1:
    # If we find more than one document with an exact match search, we can make a few more decisions based on what's in the data before we need to punt the rest to human supervision
        
        itisResult["processingMetadata"]["Detailed Results"].append({"Multi Match":url_exactMatch})
        
        # First we assemble the set of acceptedTSNs for the discovered records so that we can determine if there is only a single accepted record to follow
        # This step might need review by the ITIS team, but it seems reasonable for the records we have looked at so far
        acceptedTSNs = []
        for itisDoc in r_exactMatch["response"]["docs"]:
            if "acceptedTSN" in itisDoc.keys() and itisDoc["acceptedTSN"][0] not in acceptedTSNs:
                acceptedTSNs.append(itisDoc["acceptedTSN"][0])
        
        if len(acceptedTSNs) == 1:
        # Multiple exact matches were returned, but only one of them has an accepted TSN to follow
            itisResult["itisData"] = []
            url_tsnSearch = getITISSearchURL(acceptedTSNs[0],False,True)
            r_tsnSearch = requests.get(url_tsnSearch).json()
            itisResult["itisData"].append(packageITISJSON(r_tsnSearch["response"]["docs"][0]))
            itisResult["processingMetadata"]["Summary Result"] = "Followed Accepted TSN"
            itisResult["processingMetadata"]["Detailed Results"].append({"TSN Search":url_tsnSearch})

        else:
        # If there are multiple acceptedTSN values for multiple returned exact match records, we don't yet know what to do with these.
        # Some combination of factors in the data or a deeper level search from the source may come up with a way to make the algorithm more sophisticated.
            itisResult["processingMetadata"]["Summary Result"] = "Indeterminate Results"

    return itisResult