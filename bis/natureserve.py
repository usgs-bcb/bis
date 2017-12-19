natureServeSpeciesQueryBaseURL = "https://services.natureserve.org/idd/rest/v1/globalSpecies/list/nameSearch?name="

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
    import requests
    import xmltodict

    natureServeData = {}

    if elementGlobalID is None:
        natureServeData["result"] = False
    else:
        natureServeDict = xmltodict.parse(requests.get(speciesAPI+"&uid="+elementGlobalID).text, dict_constructor=dict)

        if "globalSpecies" not in natureServeDict["globalSpeciesList"]:
            natureServeData["result"] = False
        else:
            natureServeData["result"] = True
            
            natureServeData["availableKeys"] = list(natureServeDict["globalSpeciesList"]["globalSpecies"].keys())

            natureServeData["classification"] = natureServeDict["globalSpeciesList"]["globalSpecies"]["classification"]
            if "formalTaxonomy" in natureServeData["classification"]["taxonomy"].keys():
                natureServeData["taxonomy"] = []
                natureServeData["taxonomy"].append({"rank":"kingdom","name":natureServeData["classification"]["taxonomy"]["formalTaxonomy"]["kingdom"]})
                natureServeData["taxonomy"].append({"rank":"phylum","name":natureServeData["classification"]["taxonomy"]["formalTaxonomy"]["phylum"]})
                natureServeData["taxonomy"].append({"rank":"class","name":natureServeData["classification"]["taxonomy"]["formalTaxonomy"]["class"]})
                natureServeData["taxonomy"].append({"rank":"order","name":natureServeData["classification"]["taxonomy"]["formalTaxonomy"]["order"]})
                natureServeData["taxonomy"].append({"rank":"family","name":natureServeData["classification"]["taxonomy"]["formalTaxonomy"]["family"]})
                natureServeData["taxonomy"].append({"rank":"genus","name":natureServeData["classification"]["taxonomy"]["formalTaxonomy"]["genus"]})
                natureServeData["taxonomy"].append({"rank":"species","name":natureServeData["classification"]["names"]["scientificName"]["unformattedName"]})

            natureServeData["conservationStatus"] = natureServeDict["globalSpeciesList"]["globalSpecies"]["conservationStatus"]
            
            natureServeData["conservationStatus_us"] = {}

            _globalStatus = natureServeDict["globalSpeciesList"]["globalSpecies"]["conservationStatus"]["natureServeStatus"]["globalStatus"]
            if "nationalStatuses" in natureServeDict["globalSpeciesList"]["globalSpecies"]["conservationStatus"]["natureServeStatus"]["globalStatus"].keys():
                _nationalStatus = natureServeDict["globalSpeciesList"]["globalSpecies"]["conservationStatus"]["natureServeStatus"]["globalStatus"]["nationalStatuses"]["nationalStatus"]
            else:
                _nationalStatus = None
            
            natureServeData["conservationStatus_us"]["roundedGlobalRankCode"] = _globalStatus["roundedRank"]["code"]
            natureServeData["conservationStatus_us"]["roundedGlobalRankDescription"] = _globalStatus["roundedRank"]["description"]

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
                natureServeData["conservationStatus_us"]["usNationalStatusCode"] = _usNationalStatus["roundedRank"]["code"]

                if "subnationalStatuses" in list(_usNationalStatus.keys()):
                    _stateStatus = _usNationalStatus["subnationalStatuses"]["subnationalStatus"]
                else:
                    _stateStatus = None
                
                if _stateStatus is not None:
                    natureServeData["conservationStatus_us"]["stateStatus"] = []
                    if type(_stateStatus) is dict:
                        thisStateStatus = {}
                        thisStateStatus["stateName"] = _stateStatus["@subnationName"]
                        thisStateStatus["stateCode"] = _stateStatus["@subnationCode"]
                        thisStateStatus["roundedRankCode"] = _stateStatus["roundedRank"]["code"]
                        natureServeData["conservationStatus_us"]["stateStatus"].append(thisStateStatus)

                    elif type(_stateStatus) is list:
                        for stateStatus in _stateStatus:
                            thisStateStatus = {}
                            thisStateStatus["stateName"] = stateStatus["@subnationName"]
                            thisStateStatus["stateCode"] = stateStatus["@subnationCode"]
                            thisStateStatus["roundedRankCode"] = stateStatus["roundedRank"]["code"]
                            natureServeData["conservationStatus_us"]["stateStatus"].append(thisStateStatus)

    return natureServeData
