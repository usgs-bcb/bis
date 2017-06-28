def queryNatureServeID(scientificname):
    import requests
    from lxml import etree
    from io import StringIO
    
    natureServeSpeciesQueryBaseURL = "https://services.natureserve.org/idd/rest/v1/globalSpecies/list/nameSearch?name="
    natureServeData = requests.get(natureServeSpeciesQueryBaseURL+scientificname).text

    if natureServeData.find('<speciesSearchResultList>\r\n</speciesSearchResultList>') > 0:
        return "none"
    else:
        rawXML = natureServeData.replace('<?xml version="1.0" encoding="utf-8"?>\r\n\r\n', '')
        rawXML = rawXML.replace(' \r\n    xsi:schemaLocation="http://services.natureserve.org/docs/schemas/biodiversityDataFlow/1 http://services.natureserve.org/docs/schemas/biodiversityDataFlow/1/" \r\n    xmlns="http://services.natureserve.org/docs/schemas/biodiversityDataFlow/1" \r\n    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \r\n    schemaVersion="1.1"', '')
        f = StringIO(rawXML)
        tree = etree.parse(f)
        return tree.xpath('/speciesSearchReport/speciesSearchResultList/speciesSearchResult/globalSpeciesUid')[0].text
    
def packageNatureServePairs(speciesAPI,elementGlobalID):
    import datetime
    import requests
    from lxml import etree
    from io import StringIO
    from bis import tir

    dt = datetime.datetime.utcnow().isoformat()

    natureServeCodes = tir.tirConfig("Configuration:NatureServe Rank Code Descriptions").set_index("NatureServe Rank").to_dict()
    
    natureServePairs = '"cacheDate"=>"'+dt+'"'
    natureServePairs = natureServePairs+',"elementGlobalID"=>"'+elementGlobalID+'"'
    
    if elementGlobalID == "none":
        natureServePairs = natureServePairs+',"status"=>"Not Found"'
        return natureServePairs
    else:
        natureServeData = requests.get(speciesAPI+"&uid="+elementGlobalID).text

        strNatureServeData = natureServeData.replace('<?xml version="1.0" encoding="utf-8"?>\r\n\r\n', '')
        strNatureServeData = strNatureServeData.replace('\r\n    xsi:schemaLocation="http://services.natureserve.org/docs/schemas/biodiversityDataFlow/1 http://services.natureserve.org/docs/schemas/biodiversityDataFlow/1/"\r\n    xmlns="http://services.natureserve.org/docs/schemas/biodiversityDataFlow/1"\r\n    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\r\n    schemaVersion="1.1"', '')
        f = StringIO(strNatureServeData)
        tree = etree.parse(f)
        root = tree.getroot()
        docLength = len(root.getchildren())

        # Test the response because I've found that not everything with a global element ID seems to come back with a response here
        if docLength > 0:
            # Grab out the specific elements we want to cache
            natureServePairs = natureServePairs+',"GlobalStatusRank"=>"'+tree.xpath('/globalSpeciesList/globalSpecies/conservationStatus/natureServeStatus/globalStatus/rank/code')[0].text+'"'
            natureServePairs = natureServePairs+',"roundedGlobalStatusRankDescription"=>"'+tree.xpath('/globalSpeciesList/globalSpecies/conservationStatus/natureServeStatus/globalStatus/roundedRank/description')[0].text+'"'
            try:
                natureServePairs = natureServePairs+',"globalStatusLastReviewed"=>"'+tree.xpath('/globalSpeciesList/globalSpecies/conservationStatus/natureServeStatus/globalStatus/statusLastReviewed')[0].text+'"'
            except:
                natureServePairs = natureServePairs+',"globalStatusLastReviewed"=>"Unknown"'

            try:
                usNationalStatusRankCode = tree.xpath("//nationalStatus[@nationCode='US']/rank/code")[0].text
                usNationalStatusRankCode_rounded = usNationalStatusRankCode[:2]
                usNationalStatusRoundedRankDescription = natureServeCodes["Definition"][usNationalStatusRankCode_rounded]
                natureServePairs = natureServePairs+',"usNationalStatusRankCode"=>"'+usNationalStatusRankCode+'"'
                natureServePairs = natureServePairs+',"usNationalStatusRoundedRankDescription"=>"'+usNationalStatusRoundedRankDescription+'"'
            except:
                pass
            try:
                natureServePairs = natureServePairs+',"usNationalStatusLastReviewed"=>"'+tree.xpath("//nationalStatus[@nationCode='US']/statusLastReviewed")[0].text+'"'
            except:
                natureServePairs = natureServePairs+',"usNationalStatusLastReviewed"=>"Unknown"'

            try:
                # Loop through US states in the "subnationalStatuses" and put state names and codes into the tircache
                usStatesTree = etree.ElementTree(tree.xpath("//nationalStatus[@nationCode='US']/subnationalStatuses")[0])
                for elem in usStatesTree.iter():
                    stateName = elem.attrib.get('subnationName')
                    if isinstance(stateName, str):
                        stateRankCode = tree.xpath("//subnationalStatus[@subnationName='"+stateName+"']/rank/code")[0].text
                        stateRankCode_rounded = stateRankCode[:2]
                        stateRoundedRankDescription = natureServeCodes["Definition"][stateRankCode_rounded]
                        natureServePairs = natureServePairs+',"StateCode:'+stateName+'"=>"'+stateRankCode+'"'
                        natureServePairs = natureServePairs+',"StateStatus:'+stateName+'"=>"'+stateRoundedRankDescription+'"'
            except:
                pass
        else:
            natureServePairs = natureServePairs+',"status"=>"error"'

        return natureServePairs