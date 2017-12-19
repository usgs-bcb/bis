# Register an entity in the TIR
def tirRegistration(baseURL,recordInfoPairs):
    import requests
    insertSQL = "INSERT INTO tir.tir (registration) VALUES ('"+recordInfoPairs+"')"
    return requests.get(baseURL+"&q="+insertSQL).json()

# Basic function to insert subject ID, property, and value into tircache
def cacheToTIR(baseURL,id,infotype,pairs):
    import requests
    q_update = "UPDATE tir.tir SET "+infotype+" = '"+pairs+"' WHERE id = "+str(id)
    return requests.get(baseURL+"&q="+q_update).json()

def tirConfig(configItem):
    import requests
    import csv
    import io
    
    r = requests.get("https://www.sciencebase.gov/catalog/item/54540db7e4b0dc779374504c?format=json&fields=files").json()
    configFileURL = next((f for f in r["files"] if f["title"] == configItem), None)["url"]
    
    configFile = requests.get(configFileURL).text
    configData = list(csv.DictReader(io.StringIO(configFile), delimiter='\t'))

    return configData

def baseTIRRegistration(collection,identifier):
    from datetime import datetime
    baseRecord = {}
    baseRecord["originCollection"] = collection
    baseRecord["originID"] = identifier
    baseRecord["originDate"] = datetime.utcnow().isoformat()
    return baseRecord
