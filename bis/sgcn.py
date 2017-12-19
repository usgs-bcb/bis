def getSGCNConfigFile(configType):
    import requests
    baseItem = "https://www.sciencebase.gov/catalog/item/56d720ece4b015c306f442d5"
    
    acceptedTitles = ["Taxonomic Group Mappings","Historic 2005 SWAP National List"]
    
    if configType not in acceptedTitles:
        return None
    
    swapItemFiles = requests.get(baseItem+"?format=json&fields=files").json()
    fileURL = next((f for f in swapItemFiles["files"] if f["title"] == configType),None)["url"]

    if configType == "Taxonomic Group Mappings":
        import json
        return json.loads(requests.get(fileURL).text)

    elif configType == "Historic 2005 SWAP National List":
        historicSWAP2005 = {"AuthorityURL_2005":baseItem,"AuthorityFile_2005":fileURL}
        textFile = requests.get(fileURL, stream=True)
        historicSWAP2005["speciesList_2005"] = [s.decode("utf-8") for s in textFile.iter_lines()]
        return historicSWAP2005

