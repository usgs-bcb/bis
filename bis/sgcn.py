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
    q = "INSERT INTO sgcn.sgcn (sourceid,sourcefilename,sourcefileurl,sgcn_state,sgcn_year,scientificname_submitted,commonname_submitted,taxonomicgroup_submitted,firstyear) \
        VALUES \
        ('"+record["sourceid"]+"','"+record["sourcefilename"]+"','"+record["sourcefileurl"]+"','"+record["sgcn_state"]+"',"+str(record["sgcn_year"])+",'"+record["scientificname_submitted"]+"','"+record["commonname_submitted"]+"','"+record["taxonomicgroup_submitted"]+"',"+str(record["firstyear"])+")"
    return requests.get(baseURL+"&q="+q).json()