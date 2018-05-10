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
    
    def lookup_crossref(citation,doi=None,threshold=60):
        import requests
        
        crossRefWorksAPI = "https://api.crossref.org/works"
        mailTo = "bcb@usgs.gov"
        
        crossRefQuery = crossRefWorksAPI+"?mailto="+mailTo+"&query.bibliographic="+citation
        
        if doi is not None:
            crossRefQuery = crossRefQuery+"&filter=doi:"+doi
            
        crossRefResults = requests.get(crossRefQuery).json()
        
        if crossRefResults["status"] == "failed":
            return None
        
        if crossRefResults["message"]["total-results"] == 1 or crossRefResults["message"]["items"][0]["score"] >= threshold:
            return crossRefResults["message"]["items"][0]
        else:
            return None
            