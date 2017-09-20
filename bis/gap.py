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

# This function is similar to the first one we created for bundling GAP species information from ScienceBase but it flattens the structure to make things simpler for downstream use.
def gapToTIR_flat(sbItem):
    from datetime import datetime
    from bis import bis

    _gapTaxonomicGroups = {}
    _gapTaxonomicGroups["m"] = "mammals"
    _gapTaxonomicGroups["b"] = "birds"
    _gapTaxonomicGroups["a"] = "amphibians"
    _gapTaxonomicGroups["r"] = "reptiles"

    newItem = {}
    newItem["sbdoc"] = sbItem
    
    newItem["source"] = "GAP Species"
    newItem["registrationDate"] = datetime.utcnow().isoformat()
    newItem["followTaxonomy"] = False
    newItem["taxonomicLookupProperty"] = "tsn"

    for tag in sbItem["tags"]:
        if tag["scheme"] == "https://www.sciencebase.gov/vocab/bis/tir/scientificname":
            newItem["scientificname"] = tag["name"]
        elif tag["scheme"] == "https://www.sciencebase.gov/vocab/bis/tir/commonname":
            newItem["commonname"] = bis.stringCleaning(tag["name"])

    for identifier in sbItem["identifiers"]:
        newItem[identifier["type"]] = identifier["key"]
        if identifier["type"] == "GAP_SpeciesCode":
            newItem["taxonomicgroup"] = _gapTaxonomicGroups[identifier["key"][:1]]
    
    return newItem
