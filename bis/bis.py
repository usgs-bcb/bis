# Function for cleaning up strings (started with scientific name strings), replacing characters that mess up API data inserts into PostgreSQL via the GC2 API
def stringCleaning(text):    
    if text is None:
        return None
    
    import re

    # Specify replacements
    replacements = {}
    replacements["'"] = "''"
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
    return regex.sub(lambda mo: replacements[mo.string[mo.start():mo.end()]], text).strip()
    
def cleanScientificName(scientificname):
    import re
    from ftfy import fix_text
    
    nameString = scientificname
    
    # Fix encoding translation issues
    nameString = fix_text(nameString)

    # Remove digits, we can't work with these right now
    nameString = re.sub(r'\d+', '', nameString)

    # Get rid of strings in parentheses and brackets (these might need to be revisited eventually, but we can often find a match without this information)
    nameString = re.sub('[\(\[\"].*?[\)\]\"]', "", nameString)
    nameString = ' '.join(nameString.split())
    
    # Remove some specific substrings
    removeList = ["?","Family "]
    nameString = re.sub(r'|'.join(map(re.escape, removeList)), '', nameString)

    # Change uses of "subsp." to "ssp." for ITIS
    nameString = nameString.replace("subsp.","ssp.")
 
    # Particular words are used to describe variations or nuances in taxonomy but are not able to be used in matching names at this time
    afterChars = ["("," AND ","/"," & "," vs "," undescribed ",","," formerly "," near ","Columbia Basin","Puget Trough"," n.sp. "," n. "," sp. "," sp "," pop. "," spp. "," cf. "," ] "]
    nameString = nameString+" "
    while any(substring in nameString for substring in afterChars):
        for substring in afterChars:
            nameString = nameString.split(substring, 1)[0]
            nameString = nameString+" "

    nameString = nameString.strip()

    # Deal with cases where an "_" was used
    if nameString.find("_") != -1:
        nameString = ' '.join(nameString.split("_"))

    # Check to make sure there is actually a subspecies or variety name supplied
    if len(nameString) > 0:
        namesList = nameString.split(" ")
        if namesList[-1] in ["ssp.","var."]:
            nameString = ' '.join(namesList[:-1])
            
    # Take care of capitalizing final cross indicator
    nameString = nameString.replace(" x "," X ")
    
    return nameString.capitalize()