{
    "name" : "test0", 
    "port" : "22333", 
    "path" : "/pynode/test0", 
    "cookbook_path" : [ "pynode.cookbooks", "cookbooks", ], 
    "wsgi_app" : "/users/Kevin/Sites/Stamped/sites/stamped.com/bin/serve.py", 
    "wsgi_log" : "/tmp/wsgi.log", 
    
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
