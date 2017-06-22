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