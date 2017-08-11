def gapToTIR(sbItem):
    from datetime import datetime
    from bis import bis

    _gapTaxonomicGroups = {}
    _gapTaxonomicGroups["m"] = "mammals"
    _gapTaxonomicGroups["b"] = "birds"
    _gapTaxonomicGroups["a"] = "amphibians"
    _gapTaxonomicGroups["r"] = "reptiles"

    sbItem["source"] = "GAP Species"
    sbItem["registrationDate"] = datetime.utcnow().isoformat()
    sbItem["followTaxonomy"] = False
    sbItem["taxonomicLookupProperty"] = "tsn"

    for tag in sbItem["tags"]:
        if tag["scheme"] == "https://www.sciencebase.gov/vocab/bis/tir/scientificname":
            sbItem["scientificname"] = tag["name"]
        elif tag["scheme"] == "https://www.sciencebase.gov/vocab/bis/tir/commonname":
            sbItem["commonname"] = bis.stringCleaning(tag["name"])
    sbItem.pop("tags")

    for identifier in sbItem["identifiers"]:
        if identifier["type"] == "GAP_SpeciesCode":
            sbItem["taxonomicgroup"] = _gapTaxonomicGroups[identifier["key"][:1]]
        elif identifier["type"] == "ITIS_TSN":
            sbItem["tsn"] = identifier["key"]
    
    return sbItem
