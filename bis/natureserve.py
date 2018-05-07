class query:


    def query_natureserve(scientificname):
        import requests
        import xmltodict
        
        natureServeSpeciesQueryBaseURL = "https://services.natureserve.org/idd/rest/v1/nationalSpecies/summary/nameSearch?nationCode=US&name="
        natureServeDict = xmltodict.parse(requests.get(natureServeSpeciesQueryBaseURL+scientificname).text, dict_constructor=dict)
        
        if "species" not in natureServeDict["speciesList"].keys():
            return None
        else:
            if type(natureServeDict["speciesList"]["species"]) is list:
                validResult = [r for r in natureServeDict["speciesList"]["species"] if r["nationalScientificName"] == scientificname]
                if len(validResult) == 0:
                    return None
                else:
                    return validResult[0]
            else:
                return natureServeDict["speciesList"]["species"]
        

