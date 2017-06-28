def getWoRMSSearchURL(searchType,target):
    if searchType == "ExactName":
        return  "http://www.marinespecies.org/rest/AphiaRecordsByName/"+target+"?like=false&marine_only=false&offset=1"
    elif searchType == "FuzzyName":
        return  "http://www.marinespecies.org/rest/AphiaRecordsByName/"+target+"?like=true&marine_only=false&offset=1"
    elif searchType == "AphiaID":
        return "http://www.marinespecies.org/rest/AphiaRecordByAphiaID/"+target
    
# Pair worms properties that we want to cache
def packageWoRMSPairs(matchMethod,wormsData):
    import datetime
    dt = datetime.datetime.utcnow().isoformat()
    wormsPairs = '"cacheDate"=>"'+dt+'"'
    wormsPairs = wormsPairs+',"wormsMatchMethod"=>"'+matchMethod+'"'

    if type(wormsData) is int:
        return wormsPairs
    else:
        try:
            wormsPairs = wormsPairs+',"AphiaID"=>"'+str(wormsData['AphiaID'])+'"'
        except:
            wormsPairs = wormsPairs+',"AphiaID"=>"None"'
        wormsPairs = wormsPairs+',"scientificname"=>"'+wormsData['scientificname']+'"'
        wormsPairs = wormsPairs+',"status"=>"'+wormsData['status']+'"'
        wormsPairs = wormsPairs+',"rank"=>"'+wormsData['rank']+'"'
        wormsPairs = wormsPairs+',"valid_name"=>"'+wormsData['valid_name']+'"'
        wormsPairs = wormsPairs+',"lsid"=>"'+wormsData['lsid']+'"'
        wormsPairs = wormsPairs+',"isMarine"=>"'+str(wormsData['isMarine'])+'"'
        wormsPairs = wormsPairs+',"isBrackish"=>"'+str(wormsData['isBrackish'])+'"'
        wormsPairs = wormsPairs+',"isFreshwater"=>"'+str(wormsData['isFreshwater'])+'"'
        wormsPairs = wormsPairs+',"isTerrestrial"=>"'+str(wormsData['isTerrestrial'])+'"'
        wormsPairs = wormsPairs+',"isExtinct"=>"'+str(wormsData['isExtinct'])+'"'
        wormsPairs = wormsPairs+',"match_type"=>"'+wormsData['match_type']+'"'
        wormsPairs = wormsPairs+',"modified"=>"'+wormsData['modified']+'"'
        try:
            wormsPairs = wormsPairs+',"valid_AphiaID"=>"'+str(wormsData['valid_AphiaID'])+'"'
            wormsPairs = wormsPairs+',"kingdom"=>"'+wormsData['kingdom']+'"'
            wormsPairs = wormsPairs+',"phylum"=>"'+wormsData['phylum']+'"'
            wormsPairs = wormsPairs+',"class"=>"'+wormsData['class']+'"'
            wormsPairs = wormsPairs+',"order"=>"'+wormsData['order']+'"'
            wormsPairs = wormsPairs+',"family"=>"'+wormsData['family']+'"'
            wormsPairs = wormsPairs+',"genus"=>"'+wormsData['genus']+'"'
        except:
            pass

        return wormsPairs