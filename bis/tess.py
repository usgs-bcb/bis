def queryTESSbyTSN(tsn):
    import requests
    tessSpeciesQueryByTSNBaseURL = "https://ecos.fws.gov/ecp0/TessQuery?request=query&xquery=/SPECIES_DETAIL[TSN="
    return requests.get(tessSpeciesQueryByTSNBaseURL+tsn+"]").text

def packageTESSPairs(tsn,tessData):
    import datetime
    from lxml import etree
    from io import StringIO
    dt = datetime.datetime.utcnow().isoformat()
    tessPairs = '"cacheDate"=>"'+dt+'"'
    tessPairs = tessPairs+',"tsn"=>"'+tsn+'"'

    if tessData.find('<results/>') > 0:
        tessPairs = tessPairs+',"result"=>"none"'
    else:
        try:
            rawXML = tessData.replace('<?xml version="1.0" encoding="iso-8859-1"?>', '')
            f = StringIO(rawXML)
            tree = etree.parse(f)
            tessPairs = tessPairs+',"result"=>"success"'
            tessPairs = tessPairs+',"entityId"=>"'+tree.xpath('/results/SPECIES_DETAIL/ENTITY_ID')[0].text+'"'
            tessPairs = tessPairs+',"SpeciesCode"=>"'+tree.xpath('/results/SPECIES_DETAIL/SPCODE')[0].text+'"'
            tessPairs = tessPairs+',"CommonName"=>"'+tree.xpath('/results/SPECIES_DETAIL/COMNAME')[0].text+'"'
            tessPairs = tessPairs+',"PopulationDescription"=>"'+tree.xpath('/results/SPECIES_DETAIL/POP_DESC')[0].text+'"'
            tessPairs = tessPairs+',"Status"=>"'+tree.xpath('/results/SPECIES_DETAIL/STATUS')[0].text+'"'
            tessPairs = tessPairs+',"StatusText"=>"'+tree.xpath('/results/SPECIES_DETAIL/STATUS_TEXT')[0].text+'"'
            rListingDate = tree.xpath('/results/SPECIES_DETAIL/LISTING_DATE')
            if len(rListingDate) > 0:
                tessPairs = tessPairs+',"ListingDate"=>"'+rListingDate[0].text+'"'
            tessPairs = tessPairs.replace("\'","''").replace(";","|").replace("--","-")
        except:
            tessPairs = tessPairs+',"result"=>"error"'

    return tessPairs
