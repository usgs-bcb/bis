class ResearchReferenceLibrary:
    
    def register_citation(registryContainer,citationString,source,url=None):
        import hashlib
        from datetime import datetime
        
        result = {}
        
        hash_id = hashlib.md5(citationString.encode()).hexdigest()
        
        existingRecord = registryContainer.find_one({"_id":hash_id},{"Sources":1})
        
        if existingRecord is None:
            newCitation = {}
            newCitation["_id"] = hash_id
            newCitation["Citation String"] = citationString
            newCitation["Sources"] = [{"source":source,"date":datetime.utcnow().isoformat()}]
            if url is not None:
                newCitation["url"] = url
            registryContainer.insert_one(newCitation)
            result = {"status":"ok","_id":hash_id,"message":"New citation registered."}
        else:
            existingSource = [s for s in existingRecord["Sources"] if s["source"] == source]
            if len(existingSource) > 0:
                result = {"status":"failed","_id":existingRecord["_id"],"message":"Citation string was already registered for this source."}
            else:
                newSources = existingRecord["Sources"]
                newSources.append({"source":source,"date":datetime.utcnow().isoformat()})
                registryContainer.update({"_id":existingSource["_id"]},{"$set":{"Sources":newSources}})
                result = {"status":"ok","_id":existingRecord["_id"],"message":"Citation string already registered; new source added."}

        return result

    
    def ref_link_data(url):
        import requests
        from datetime import datetime
        
        response = {"Date Checked":datetime.utcnow().isoformat(),"Link Checked":url}
        
        try:
            response["Link Response"] = requests.get(url, headers={"Accept":"application/json"}).json()
            response["Success"] = True
        except:
            response["Success"] = False
        
        return response
    
    
    def lookup_crossref(citation,doi=None,threshold=60):
        import requests
        from datetime import datetime
        
        crossRefDoc = {"Success":False,"Check Date":datetime.utcnow().isoformat()}
        
        crossRefWorksAPI = "https://api.crossref.org/works"
        mailTo = "bcb@usgs.gov"
        
        crossRefQueryNoDOI = crossRefWorksAPI+"?mailto="+mailTo+"&query.bibliographic="+citation
        if doi is None:
            crossRefQuery = crossRefQueryNoDOI
        else:
            crossRefQuery = crossRefQueryNoDOI+"&filter=doi:"+doi
        
        crossRefDoc["Query URL"] = crossRefQuery
        crossRefResults = requests.get(crossRefQuery).json()
        
        if "items" in crossRefResults["message"].keys() and len(crossRefResults["message"]["items"]) > 0 and crossRefResults["message"]["items"][0]["score"] >= threshold:
            crossRefDoc["Success"] = True
            crossRefDoc["Score"] = crossRefResults["message"]["items"][0]["score"]
            crossRefDoc["Record"] = crossRefResults["message"]["items"][0]
        else:
            if doi is not None:
                crossRefDoc["Query URL"] = crossRefQueryNoDOI
                crossRefResults = requests.get(crossRefQueryNoDOI).json()
                if "items" in crossRefResults["message"].keys() and len(crossRefResults["message"]["items"]) > 0 and crossRefResults["message"]["items"][0]["score"] >= threshold:
                    crossRefDoc["Success"] = True
                    crossRefDoc["Score"] = crossRefResults["message"]["items"][0]["score"]
                    crossRefDoc["Record"] = crossRefResults["message"]["items"][0]

        return crossRefDoc