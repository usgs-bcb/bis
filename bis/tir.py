def tirRegistration(baseURL,recordInfoPairs):
    import requests
    insertSQL = "INSERT INTO tir.tir (registration) VALUES ('"+recordInfoPairs+"')"
    return requests.get(baseURL+"&q="+insertSQL).json()