natureServeSpeciesQueryBaseURL = "https://services.natureserve.org/idd/rest/v1/globalSpecies/list/nameSearch?name="

def getNatureServeNameSearchURL(scientificname):
    return natureServeSpeciesQueryBaseURL+scientificname

def searchDict(d, key, default=None):
    stack = [iter(d.items())]
    while stack:
        for k, v in stack[-1]:
            if isinstance(v, dict):
                stack.append(iter(v.items()))
                break
            elif k == key:
                return v
        else:
            stack.pop()
    return default
    
def queryNatureServeID(scientificname):
    import requests
    import xmltodict
    
    natureServeSpeciesQueryBaseURL = "https://services.natureserve.org/idd/rest/v1/globalSpecies/list/nameSearch?name="
    natureServeDict = xmltodict.parse(requests.get(natureServeSpeciesQueryBaseURL+scientificname).text, dict_constructor=dict)
    
    if natureServeDict["speciesSearchReport"]["speciesSearchResultList"] is None:
        return None
    else:
        return searchDict(natureServeDict,"globalSpeciesUid")

def packageNatureServeJSON(speciesAPI,elementGlobalID):
    from datetime import datetime
    import requests
    import xmltodict
    from bis import tir

    natureServeData = {}
    natureServeData["dateCached"] = datetime.utcnow().isoformat()
    natureServeData["result"] = False
    natureServeData["elementGlobalID"] = elementGlobalID

    natureServeCodes = tir.tirConfig("Configuration:NatureServe Rank Code Descriptions").set_index("NatureServe Rank").to_dict()
    
    if elementGlobalID is None:
        natureServeData["status"] = "Not Found"
    else:
        natureServeDict = xmltodict.parse(requests.get(speciesAPI+"&uid="+elementGlobalID).text, dict_constructor=dict)

        if "globalSpecies" not in natureServeDict["globalSpeciesList"]:
            natureServeData["status"] = "Not Found"
        else:
            natureServeData["result"] = True

            _globalStatus = natureServeDict["globalSpeciesList"]["globalSpecies"]["conservationStatus"]["natureServeStatus"]["globalStatus"]
            _nationalStatus = natureServeDict["globalSpeciesList"]["globalSpecies"]["conservationStatus"]["natureServeStatus"]["globalStatus"]["nationalStatuses"]["nationalStatus"]
            
            natureServeData["roundedGlobalRankCode"] = _globalStatus["roundedRank"]["code"]
            natureServeData["roundedGlobalRankDescription"] = _globalStatus["roundedRank"]["description"]

            _usNationalStatus = None
            if type(_nationalStatus) is list:
                for nationalStatusRecord in _nationalStatus:
                    if nationalStatusRecord["@nationCode"] == "US":
                        _usNationalStatus = nationalStatusRecord
                        break
            elif type(_nationalStatus) is dict:
                if _nationalStatus["@nationCode"] == "US":
                    _usNationalStatus = _nationalStatus
                
            if _usNationalStatus is not None:
                natureServeData["usNationalStatusCode"] = _usNationalStatus["roundedRank"]["code"]
                try:
                    natureServeData["usNationalStatusDescription"] = natureServeCodes["Definition"][natureServeData["usNationalStatusCode"]]
                except:
                    natureServeData["usNationalStatusDescription"] = natureServeData["usNationalStatusCode"]
                
                if "subnationalStatuses" in list(_usNationalStatus.keys()):
                    _stateStatus = _usNationalStatus["subnationalStatuses"]["subnationalStatus"]
                else:
                    _stateStatus = None
                
                if _stateStatus is not None:
                    natureServeData["stateStatus"] = []
                    if type(_stateStatus) is dict:
                        thisStateStatus = {}
                        thisStateStatus["stateName"] = _stateStatus["@subnationName"]
                        thisStateStatus["stateCode"] = _stateStatus["@subnationCode"]
                        thisStateStatus["roundedRankCode"] = _stateStatus["roundedRank"]["code"]
                        try:
                            thisStateStatus["roundedRankDescription"] = natureServeCodes["Definition"][thisStateStatus["roundedRankCode"]]
                        except:
                            thisStateStatus["roundedRankDescription"] = thisStateStatus["roundedRankCode"]
                        natureServeData["stateStatus"].append(thisStateStatus)

                    elif type(_stateStatus) is list:
                        for stateStatus in _stateStatus:
                            thisStateStatus = {}
                            thisStateStatus["stateName"] = stateStatus["@subnationName"]
                            thisStateStatus["stateCode"] = stateStatus["@subnationCode"]
                            thisStateStatus["roundedRankCode"] = stateStatus["roundedRank"]["code"]
                            try:
                                thisStateStatus["roundedRankDescription"] = natureServeCodes["Definition"][thisStateStatus["roundedRankCode"]]
                            except:
                                thisStateStatus["roundedRankDescription"] = thisStateStatus["roundedRankCode"]
                            natureServeData["stateStatus"].append(thisStateStatus)

    return natureServeData