{
    "name" : "test0", 
    "port" : "22333", 
    "path" : "/pynode/test0", 
    "cookbook_path" : [ "pynode.cookbooks", ], 
    
    "python" : {
        "requirements" : [
            "fabric", 
            "BeautifulSoup", 
            "boto", 
            "xlrd", 
            "pymongo", 
            "flask", 
            "gunicorn", 
            "gevent", 
        ], 
    }, 
    
    "recipes" : [
        "pythonenv", 
    ], 
}
