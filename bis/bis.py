# Function for cleaning up strings (started with scientific name strings), replacing characters that mess up API data inserts into PostgreSQL via the GC2 API
def stringCleaning(text):    
    if text is None:
        return None
    
    import re

    # Specify replacements
    replacements = {}
    replacements["'"] = "' || chr(39) || '"
    replacements["--"] = "' || chr(45)chr(45) || '"
    replacements["&"] = "' || chr(38) || '"
    replacements['"'] = "' || chr(34) || '"
    replacements[";"] = "' || chr(59) || '"
    replacements["#"] = "' || chr(35) || '"
    
    # Compile the expressions
    regex = re.compile("(%s)" % "|".join(map(re.escape, replacements.keys())))

    # Strip the text
    text = text.strip()

    # Process replacements
    return regex.sub(lambda mo: replacements[mo.string[mo.start():mo.end()]], text)

# There are a few things that we've found in scientific name strings that, if removed or modified, will result in a valid taxon name string for the name lookup in ITIS and other places
def cleanScientificName(scientificname):
    import re

    # Get rid of ? and * - they might mean something, but...
    for character in ["?","*"]:
        scientificname = scientificname.replace(character, "")

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
        
    # If the name did not include an actual subspecies/variety name, get rid of the indicator
    if len(scientificname) > 0:
        if scientificname.split()[-1] in ["ssp.","ssp","var."]:
            scientificname = scientificname.replace("ssp.", "").replace("ssp","").replace("var.","")
    
    # Get rid of characters after certain characters to produce a shorter (and sometimes higher taxonomy) name string compatible with the ITIS service
    afterChars = ["(", " sp.", " spp.", " sp ", " spp ", " n.", " pop.", "l.", "/"]
    # Add a space at the end for this step to help tease out issues with split characters ending the string (could probably be better as re)
    scientificname = scientificname+" "
    for char in afterChars:
        scientificname = scientificname.split(char, 1)[0]
    
    # Get rid of any lingering periods
    scientificname = scientificname.replace(".", "")

    # Cleanup extra spaces
    scientificname = " ".join(scientificname.split())

    return scientificname