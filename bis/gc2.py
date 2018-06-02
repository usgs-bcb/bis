def gc2_api(apipathvar,apikeyvar=None):
    import os
    
    try:
        _baseURL = os.environ[apipathvar.upper()]
        if apikeyvar is not None:
            _baseURL = _baseURL+"?key="+os.environ[apikeyvar.upper()]
        return _baseURL
    except:
        return None