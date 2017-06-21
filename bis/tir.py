# Register an entity in the TIR
def tirRegistration(baseURL,recordInfoPairs):
    import requests
    insertSQL = "INSERT INTO tir.tir (registration) VALUES ('"+recordInfoPairs+"')"
    return requests.get(baseURL+"&q="+insertSQL).json()

# Basic function to insert subject ID, property, and value into tircache
def cacheToTIR(gid,infotype,pairs):
    import requests
    updateQ = "UPDATE tir.tir SET "+infotype+" = '"+pairs+"' WHERE gid = "+str(gid)
    r = requests.get(getBaseURL()+"&q="+updateQ).json()
    return r