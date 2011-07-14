{
    "name" : "test0", 
    "port" : "22333", 
    "path" : "/pynode/test0", 
    "cookbook_path" : [ "pynode.cookbooks", "cookbooks", ], 
    "wsgi_app" : "/stamped/sites/stamped.com/bin/serve.py", 
    
    "python" : {
        "requirements" : [
            "fabric", 
            "BeautifulSoup", 
            "boto", 
            "xlrd", 
            "pymongo", 
            "flask", 
            "gunicorn", 
            #"gevent", 
        ], 
    }, 
    
    "recipes" : [
        "stamped", 
    ], 
}
