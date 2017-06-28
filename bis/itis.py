def getITISSearchURL(searchstr):
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
    # "valid" and "accepted" usage values will further constrain the search and handle cases where the search returns more than one possible record on name
    return "http://services.itis.gov/?wt=json&rows=10&q=(usage:accepted%20OR%20usage:valid)%20AND%20"+itisTerm+":"+searchstr.replace(" ","\%20")

def packageITISPairs(matchMethod,matchString,itisDoc):
    import datetime
    from bis import bis
    itisPairs = '"cacheDate"=>"'+datetime.datetime.utcnow().isoformat()+'"'
    itisPairs = itisPairs+',"itisMatchMethod"=>"'+matchMethod+'"'
    itisPairs = itisPairs+',"itisMatchString"=>"'+bis.stringCleaning(matchString)+'"'

    if type(itisDoc) is int:
        return itisPairs
    else:
        itisPairs = itisPairs+',"createDate"=>"'+itisDoc['createDate']+'"'
        itisPairs = itisPairs+',"updateDate"=>"'+itisDoc['updateDate']+'"'
        itisPairs = itisPairs+',"tsn"=>"'+itisDoc['tsn']+'"'
        itisPairs = itisPairs+',"rank"=>"'+itisDoc['rank']+'"'
        itisPairs = itisPairs+',"nameWInd"=>"'+itisDoc['nameWInd']+'"'
        itisPairs = itisPairs+',"nameWOInd"=>"'+itisDoc['nameWOInd']+'"'
        itisPairs = itisPairs+',"usage"=>"'+itisDoc['usage']+'"'

        if 'acceptedTSN' in itisDoc:
            itisPairs = itisPairs+',"acceptedTSN"=>"'+itisDoc['acceptedTSN'][0]+'"'

        hierarchy = itisDoc['hierarchySoFarWRanks'][0]
        hierarchy = hierarchy[hierarchy.find(':$')+2:-1]
        hierarchy = '"'+hierarchy.replace(':', '"=>"').replace('$', '","')+'"'
        itisPairs = itisPairs+','+hierarchy

        if "vernacular" in itisDoc:
            vernacularList = []
            for commonName in itisDoc['vernacular']:
                commonNameElements = commonName.split('$')
                vernacularList.append('"vernacular:'+commonNameElements[2]+'"=>"'+commonNameElements[1]+'"')
            strVernacularList = ''.join(vernacularList).replace("\'", "''").replace('""','","')
            itisPairs = itisPairs+','+strVernacularList

        return itisPairs