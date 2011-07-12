{
    "name" : "test0", 
    "port" : "22333", 
    "path" : "/pynode/test0", 
    "cookbook_path" : "cookbooks", 
    
    "python" : {
        "requirements" : [
            "fabric", 
            "BeautifulSoup", 
            "boto", 
            "gevent", 
            "xlrd", 
            "pymongo", 
            "flask", 
            "gunicorn", 
        ], 
    }, 
    
    "cookbooks" : [
        "mongodb", 
    ], 
}
