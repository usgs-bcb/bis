# Function for cleaning up strings (started with scientific name strings), replacing characters that mess up API data inserts into PostgreSQL via the GC2 API
def stringCleaning(text):    
    import re

    # Specify replacements
    replacements = {}
    replacements["'"] = "''"
    replacements["--"] = ""
    replacements["&"] = "and"
    replacements['"'] = "''"
    replacements[";"] = ","
    replacements["#"] = "no."
    
    # Compile the expressions
    regex = re.compile("(%s)" % "|".join(map(re.escape, replacements.keys())))

    # Strip the text
    text = text.strip()

    # Process replacements
    return regex.sub(lambda mo: replacements[mo.string[mo.start():mo.end()]], text)

# There are a few things that we've found in scientific name strings that, if removed or modified, will result in a valid taxon name string for the name lookup in ITIS and other places
def cleanScientificName(scientificname):
    import re

    # Get rid of ? - they might mean something, but...
    scientificname = scientificname.replace("?", "")

    # Get rid of text in parens, brackets, or single quotes; this is a design decision to potentially do away with information that might be important, but it gets retained in the original records
    scientificname = re.sub("[\(\[\'].*?[\'\)\]]", "", scientificname)
    
    # Clean up all upper case strings because the ITIS service doesn't like them
    if any(x.isupper() for x in scientificname[-(len(scientificname)-1):]):
        scientificname = scientificname.lower().capitalize()

    # Replace "subsp." with "ssp." in order to make the subspecies search work
    scientificname = scientificname.replace("subsp.", "ssp.")
    
    # Get rid of any numbers, we can't really do anything with those
    nameWODigits = ""
    for word in scientificname.split():
        if not any(c.isdigit() for c in word):
            nameWODigits = nameWODigits+" "+word
    scientificname = nameWODigits
        
    # If the name did not include an actual subspecies name, get rid of the indicator
    if len(scientificname) > 0:
        if scientificname.split()[-1] in ["ssp.","ssp"]:
            scientificname = scientificname.replace("ssp.", "").replace("ssp","")
    
    # Get rid of characters after certain characters to produce a shorter (and sometimes higher taxonomy) name string compatible with the ITIS service
    afterChars = ["(", " sp.", " spp.", " sp ", " spp ", " n.", " pop.", "l.", "/"]
    # Add a space at the end for this step to help tease out issues with split characters ending the string (could probably be better as re)
    scientificname = scientificname+" "
    for char in afterChars:
        scientificname = scientificname.split(char, 1)[0]

    # Cleanup extra spaces
    scientificname = " ".join(scientificname.split())

    return scientificname