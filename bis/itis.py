def getITISSearchURL(searchstr,fuzzy=False,validAccepted=True):
    fuzzyLevel = "~0.5"
    
    # Default to using name without indicator as the search term
    itisTerm = "nameWOInd"
    
    # "var." and "ssp." indicate that the string has population and variation indicators and should use the WInd service
    if searchstr.find("var.") > 0 or searchstr.find("ssp.") > 0:
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
    from bis import bis
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
                thisCommonName["name"] = bis.stringCleaning(commonName.split('$')[1])
                thisCommonName["language"] = commonName.split('$')[2]
                itisDoc["commonnames"].append(thisCommonName)
            itisDoc.pop("vernacular",None)
        
        # Add the new ITIS doc to the ITIS data structure and return 
        itisData.update(itisDoc)

    return itisData
