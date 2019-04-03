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
        

def getTaxGroup(taxonomy,mappings):
    sgcnCheck = None
    for taxLevel in taxonomy:
        sgcnCheck = next((t for t in mappings if t["rank"] == taxLevel["rank"] and t["name"] == taxLevel["name"]), None)
        if sgcnCheck is not None:
            return sgcnCheck["sgcntaxonomicgroup"]
    if sgcnCheck is None:
        return None


def sgcn_source_item_metadata(item):
    from datetime import datetime

    sourceItem = {"processingMetadata": {}}
    sourceItem["processingMetadata"]["sourceID"] = item["link"]["url"]
    sourceItem["processingMetadata"]["dateProcessed"] = datetime.utcnow().isoformat()

    sgcn_year = next((d for d in item["dates"] if d["type"] == "Collected"), None)["dateString"]
    if sgcn_year is None:
        return None
    else:
        sourceItem["processingMetadata"]["sgcn_year"] = sgcn_year

    sgcn_state = next((t for t in item["tags"] if t["type"] == "Place"), None)["name"]
    if sgcn_state is None:
        return None
    else:
        sourceItem["processingMetadata"]["sgcn_state"] = sgcn_state

    processFile = next((f for f in item["files"] if f["title"] == "Process File"), None)
    if processFile is None:
        return None
    else:
        sourceItem["processingMetadata"]["processFileURL"] = processFile["url"]
        sourceItem["processingMetadata"]["processFileName"] = processFile["name"]
        sourceItem["processingMetadata"]["processFileUploadDate"] = datetime.strptime(
            processFile["dateUploaded"].split("T")[0], "%Y-%m-%d")
        return sourceItem


def process_sgcn_source_file(sourceItem):
    import requests,csv,io

    sourceItem["sourceData"] = []
    sourceFileContents = requests.get(sourceItem["processingMetadata"]["processFileURL"]).text
    inputData = list(csv.DictReader(io.StringIO(sourceFileContents), delimiter='\t'))
    for record in inputData:
        sourceItem["sourceData"].append({k.lower(): v for k, v in record.items()})
    sourceItem["processingMetadata"]["sourceRecordCount"] = len(sourceItem["sourceData"])
    
    return sourceItem
    

def package_source_name(name):
    import bis
    from datetime import datetime

    d_uniqueName = {}
    d_uniqueName["nameProcessingMetadata"] = {}
    d_uniqueName["nameProcessingMetadata"]["processingAlgorithmName"] = "bis.cleanScientificName"
    d_uniqueName["nameProcessingMetadata"]["processingAlgorithmURI"] = "https://github.com/usgs-bcb/bis/blob/master/bis/bis.py"
    d_uniqueName["nameProcessingMetadata"]["creationDate"] = datetime.utcnow().isoformat()
    d_uniqueName["nameProcessingMetadata"]["sourceCollection"] = "SGCN Source Data"
    d_uniqueName["ScientificName_original"] = name
    d_uniqueName["ScientificName_clean"] = bis.cleanScientificName(name)
    return d_uniqueName


def sgcn_source_summary(sgcnSource,ScientificName_original):
    pipeline = [
        {"$match":{"processingMetadata.legacy":{"$exists":False}}},
        {"$unwind":{"path":"$sourceData"}},
        {"$match":{"sourceData.scientific name":ScientificName_original}},
        {"$group":{"_id":"$processingMetadata.sgcn_year","states":{"$addToSet":"$processingMetadata.sgcn_state"},"Common Names":{"$addToSet":"$sourceData.common name"}}},
        {"$sort":{"_id":-1}}
    ]
    
    SourceDataSummary = {"State Submissions":{},"Common Names":[]}
    for record in sgcnSource.aggregate(pipeline):
        for commonName in record["Common Names"]:
            if commonName.strip() not in SourceDataSummary["Common Names"]:
                SourceDataSummary["Common Names"].append(commonName.strip())
        if record["_id"] not in SourceDataSummary["State Submissions"].keys():
            SourceDataSummary["State Submissions"][record["_id"]] = record["states"]
        else:
            SourceDataSummary["State Submissions"][record["_id"]].append(record["states"])
            
    for year,states in SourceDataSummary["State Submissions"].items():
        SourceDataSummary["State Submissions"][year] = list(set(states))
        SourceDataSummary["State Submissions"][year].sort()
        
    return SourceDataSummary


def sgcn_state_submissions(sgcnTIRProcessCollection,submittedNames):
    
    states = {"2005":{"included":False,"State List":[],"number":0},"2015":{"included":False,"State List":[],"number":0}}
    
    for tirRecord in sgcnTIRProcessCollection.find({"ScientificName_original":{"$in":submittedNames}},{"Source Data Summary":1}):
        try:
            states["2005"]["State List"] = states["2005"]["State List"]+tirRecord["Source Data Summary"]["State Submissions"]["2005"]
        except:
            pass
        try:
            states["2015"]["State List"] = states["2015"]["State List"]+tirRecord["Source Data Summary"]["State Submissions"]["2015"]
        except:
            pass
    
    if len(states["2005"]["State List"]) > 0:
        states["2005"]["included"] = True
        states["2005"]["State List"] = list(set(states["2005"]["State List"]))
        states["2005"]["State List"].sort()
        states["2005"]["number"] = len(states["2005"]["State List"])

    if len(states["2015"]["State List"]) > 0:
        states["2015"]["included"] = True
        states["2015"]["State List"] = list(set(states["2015"]["State List"]))
        states["2015"]["State List"].sort()
        states["2015"]["number"] = len(states["2015"]["State List"])

    return states
    
    
def sgcn_tess_synthesis(sgcnTIRProcessCollection,submittedNames):
    
    tessSynthesis = []
    
    for tirRecord in sgcnTIRProcessCollection.find({"$and":[{"ScientificName_original":{"$in":submittedNames}},{"tess.processingMetadata.matchMethod":{"$ne":"Not Matched"}}]},{"tess":1}):
        if len([d for d in tessSynthesis if 'tessData' in tirRecord["tess"] and d["ENTITY_ID"] == tirRecord["tess"]["tessData"]["ENTITY_ID"]]) == 0:
            if "tessData" in tirRecord["tess"]:
                tessSynthesis.append(tirRecord["tess"]["tessData"])
            
    if len(tessSynthesis) == 0:
        return None
    else:
        tessRecord = {"Number of TESS Records":len(tessSynthesis),"TESS Records":tessSynthesis}
        tessRecord["Primary Listing Status"] = "Undetermined (check data)"
        tessRecord["Primary Listing Date"] = "Undetermined (check data)"
        if len(tessSynthesis) == 1:
            try:
                primaryListingStatus = [r for r in tessSynthesis[0]["listingStatus"] if r["POP_DESC"].lower() == "wherever found"]
                if len(primaryListingStatus) == 1:
                    tessRecord["Primary Listing Status"] = primaryListingStatus[0]["STATUS"]
                    if "LISTING_DATE" in primaryListingStatus[0].keys():
                        tessRecord["Primary Listing Date"] = primaryListingStatus[0]["LISTING_DATE"]
                else:
                    tessRecord["Primary Listing Status"] = tessSynthesis[0]["listingStatus"][0]["STATUS"]
                    if "LISTING_DATE" in tessSynthesis[0]["listingStatus"][0].keys():
                        tessRecord["Primary Listing Date"] = tessSynthesis[0]["listingStatus"][0]["LISTING_DATE"]
            except:
                pass

        return tessRecord
        
        
def sgcn_natureserve_summary(sgcnTIRCollection,ScientificName):
    import urllib.request
    import requests,json
    
    nsCodesFileName = "NS_CodeDescriptions.json"
    
    try:
        nsCodes = json.loads(open(nsCodesFileName).read())
    except:
        sgcnBaseItem = requests.get("https://www.sciencebase.gov/catalog/item/56d720ece4b015c306f442d5?format=json&fields=files").json()
        nsCodesFileURL = next((f for f in sgcnBaseItem["files"] if f["title"] == "NatureServe National Conservation Status Descriptions"), None)["url"]
        urllib.request.urlretrieve(nsCodesFileURL, nsCodesFileName)
        nsCodes = json.loads(open(nsCodesFileName).read())

    natureServeRecord = sgcnTIRCollection.find_one({"Scientific Name":ScientificName},{"NatureServe":1})
    
    if natureServeRecord is None or "NatureServe Record" not in natureServeRecord["NatureServe"].keys():
        return {"NatureServe Summary":{"result":False}}
    else:
        nsSummaryRecord = {"result":True,"Date Cached":natureServeRecord["NatureServe"]["processingMetadata"]["dateProcessed_search"]}
        nsSummaryRecord["Element National ID"] = natureServeRecord["NatureServe"]["NatureServe Record"]["@uid"]
        nsSummaryRecord["Element Global ID"] = natureServeRecord["NatureServe"]["NatureServe Record"]["natureServeGlobalConcept"]["@uid"]
        nsSummaryRecord["Rounded National Conservation Status"] = natureServeRecord["NatureServe"]["NatureServe Record"]["roundedNationalConservationStatus"]
        nsSummaryRecord["National Conservation Status Description"] = nsCodes[nsSummaryRecord["Rounded National Conservation Status"]]
        nsSummaryRecord["Rounded Global Conservation Status"] = natureServeRecord["NatureServe"]["NatureServe Record"]["natureServeGlobalConcept"]["roundedGlobalConservationStatus"]
        nsSummaryRecord["Reference URL"] = natureServeRecord["NatureServe"]["NatureServe Record"]["natureServeGlobalConcept"]["natureServeExplorerURI"]
        try:
            nsSummaryRecord["National Status Last Reviewed"] = natureServeRecord["NatureServe"]["NatureServe Record"]["nationalConservationStatus"]["@lastReviewedDate"]
        except:
            nsSummaryRecord["National Status Last Reviewed"] = "Unknown"
        try:
            nsSummaryRecord["National Status Last Changed"] = natureServeRecord["NatureServe"]["NatureServe Record"]["nationalConservationStatus"]["@lastChangedDate"]
        except:
            nsSummaryRecord["National Status Last Changed"] = "Unknown"
        return {"NatureServe Summary":nsSummaryRecord}
        
        
def set_legacy_sourcefile_flag(sgcnSource):
    pipeline = [
        {"$group":{
            "_id":{"state":"$processingMetadata.sgcn_state","year":"$processingMetadata.sgcn_year"},
            "files":{"$addToSet":"$processingMetadata.processFileURL"},
            "dates":{"$addToSet":"$processingMetadata.processFileUploadDate"}
        }},
        {"$match":{"files.1":{"$exists":True}}}
    ]

    for record in sgcnSource.aggregate(pipeline):
        record["dates"].sort(reverse=True)
        sgcnSource.update_many({"$and":[{"processingMetadata.sgcn_state":record["_id"]["state"]},{"processingMetadata.sgcn_year":record["_id"]["year"]},{"processingMetadata.processFileUploadDate":{"$in":record["dates"][1:]}}]},{"$set":{"processingMetadata.legacyFile":True}})
        
