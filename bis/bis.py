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