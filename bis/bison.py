def getBISONSearchURL(queryType,criteria):
    from bis import bis

    _baseURL = "https://bison.usgs.gov/api/search.json?count=1&"

    if queryType != "TSN":
        return _baseURL+"type=scientific_name&species="+bis.stringCleaning(criteria)
    else:
        return _baseURL+"tsn="+str(criteria)
    
