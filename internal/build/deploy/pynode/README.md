
PyNode:
    * host
    * port
    * config file
        * name (defaults to host:port)
        * virtualenv directory (defaults to /pynode/name)
        * pip requirements
        * script to run

=>

    * PyNode instance running on host:port
    * private mongod instance running on host:port+16


PyNode directory
    * how to communicate between nodes?
        * PyNode server => talks to clients via fabric
        * clients are initialized when connected to a server
        * would really like to utilize MongoDB's master / slave promotion
          for master / slave PyNodes
        * fabric
    * host+port+name
    * each node runs an instance of MongoDB by default?
    * virtualenv+pip
    * python package*
        * requirements.txt
    * git?
    * service*
    * script*

