# Get the current record count for an SGCN state and year
def getCurrentRecordCount(baseURL,sgcn_state,sgcn_year):
    import requests
    r = requests.get(baseURL+"&q=SELECT COUNT(*) AS sumstateyear FROM sgcn.sgcn WHERE sgcn_year="+str(sgcn_year)+" AND sgcn_state='"+sgcn_state+"'").json()
    return r["features"][0]["properties"]["sumstateyear"]

# Flush a particular state and year from the sgcn table
def clearStateYear(baseURL,sgcn_state,sgcn_year):
    import requests
    return requests.get(baseURL+"&q=DELETE FROM sgcn.sgcn WHERE sgcn_year="+str(sgcn_year)+" AND sgcn_state='"+sgcn_state+"'").json()

# Insert a record into the SGCN table
def insertSGCNData(baseURL,record):
    import requests
    from datetime import datetime

    q = "INSERT INTO sgcn.sgcn (sourceid,sourcefilename,sourcefileurl,sgcn_state,sgcn_year,scientificname_submitted,commonname_submitted,taxonomicgroup_submitted,firstyear,dateinserted) \
        VALUES \
        ('"+record["sourceid"]+"','"+record["sourcefilename"]+"','"+record["sourcefileurl"]+"','"+record["sgcn_state"]+"',"+str(record["sgcn_year"])+",'"+record["scientificname_submitted"]+"','"+record["commonname_submitted"]+"','"+record["taxonomicgroup_submitted"]+"',"+str(record["firstyear"])+",'"+datetime.utcnow().isoformat()+"')"
    return requests.get(baseURL+"&q="+q).json()

# Get date inserted for SGCN state/year
def getDateInserted(baseURL,sgcn_state,sgcn_year):
    import requests
    r = requests.get(baseURL+"&q=SELECT dateinserted FROM sgcn.sgcn WHERE sgcn_year="+str(sgcn_year)+" AND sgcn_state='"+sgcn_state+"' LIMIT 1").json()
    if len(r["features"]) > 0:
        return r["features"][0]["properties"]["dateinserted"]
    else:
        return "1992-08-08"
    
def getSGCNCommonName(baseURL,scientificname):
    import requests
    _commonname = None
    q = "SELECT commonname_submitted FROM sgcn.sgcn WHERE scientificname_submitted = '"+scientificname+"' AND commonname_submitted <> '' ORDER BY dateinserted DESC LIMIT 1"
    r = requests.get(baseURL+"&q="+q).json()
    if len(r["features"]) > 0:
        _commonname = r["features"][0]["properties"]["commonname_submitted"]
    return _commonname

def getSGCNTaxonomicGroup(baseURL,scientificname):
    import requests
    from bis import bis
    _taxonomicgroup = None
    q = "SELECT taxonomicgroup_submitted FROM sgcn.sgcn WHERE scientificname_submitted = '"+bis.stringCleaning(scientificname)+"' AND taxonomicgroup_submitted <> '' ORDER BY dateinserted ASC LIMIT 1"
    r = requests.get(baseURL+"&q="+q).json()
    if len(r["features"]) > 0:
        _taxonomicgroup = r["features"][0]["properties"]["taxonomicgroup_submitted"]
    return _taxonomicgroup