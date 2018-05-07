class ResearchReferenceLibrary:
    
    def register_citation(registryContainer,citationString,sourceCollection):
        import hashlib
        from datetime import datetime
        
        result = {}
        
        hash_id = hashlib.md5(citationString.encode()).hexdigest()
        
        existingRecord = registryContainer.find_one({"_id":hash_id},{"Sources":1})
        
        if existingRecord is None:
            registryContainer.insert_one({"_id":hash_id,"Sources":[{"collection":sourceCollection,"date":datetime.utcnow().isoformat()}],"Citation String":citationString})
            result = {"status":"ok","_id":hash_id,"message":"New citation registered."}
        else:
            existingSource = [s for s in existingRecord["Sources"] if s["collection"] == sourceCollection]
            if len(existingSource) > 0:
                result = {"status":"failed","_id":existingRecord["_id"],"message":"Citation string was already registered for this source."}
            else:
                newSources = existingRecord["Sources"]
                newSources.append({"collection":sourceCollection,"date":datetime.utcnow().isoformat()})
                registryContainer.update({"_id":existingSource["_id"]},{"$set":{"Sources":newSources}})
                result = {"status":"ok","_id":existingRecord["_id"],"message":"Citation string already registered; new source added."}

        return result