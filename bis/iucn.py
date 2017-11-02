# The APIs for all of these functions require the addition of our IUCN token accessed through the bis2 package to operate.

def getSpeciesSearchURL(scientificname):
    return "http://apiv3.iucnredlist.org/api/v3/species/"+scientificname