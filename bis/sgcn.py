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


def sgcn_source_summary(sgcnSource,ScientificName_original):
    pipeline = [
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
        if len([d for d in tessSynthesis if d["ENTITY_ID"] == tirRecord["tess"]["tessData"]["ENTITY_ID"]]) == 0:
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
    natureServeRecord = sgcnTIRCollection.find_one({"Scientific Name":ScientificName},{"NatureServe":1})
    
    if natureServeRecord is None or "NatureServe Record" not in natureServeRecord["NatureServe"].keys():
        return {"NatureServe Summary":{"result":False}}
    else:
        nsSummaryRecord = {"result":True,"Date Cached":natureServeRecord["NatureServe"]["processingMetadata"]["dateProcessed_search"]}
        nsSummaryRecord["Element National ID"] = natureServeRecord["NatureServe"]["NatureServe Record"]["@uid"]
        nsSummaryRecord["Element Global ID"] = natureServeRecord["NatureServe"]["NatureServe Record"]["natureServeGlobalConcept"]["@uid"]
        nsSummaryRecord["Rounded National Conservation Status"] = natureServeRecord["NatureServe"]["NatureServe Record"]["roundedNationalConservationStatus"]
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