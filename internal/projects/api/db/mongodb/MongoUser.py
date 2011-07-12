#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from MongoDB import Mongo
from AUserDB import AUserDB
from User import User

class MongoUser(AUserDB, Mongo):
        
    COLLECTION = 'users'
        
    SCHEMA = {
        '_id': object,
        'first_name': basestring,
        'last_name': basestring,
        'username': basestring,
        'email': basestring,
        'password': basestring,
        'img': basestring,
        'locale': basestring,
        'timestamp': basestring,
        'website': basestring,
        'bio': basestring,
        'colors': {
            'primary_color': basestring,
            'secondary_color': basestring
        },
        'linked_accounts': {
            'itunes': basestring
        },
        'flags': {
            'privacy': bool,
            'flagged': bool,
            'locked': bool
        },
        'stats': {
            'total_stamps': int,
            'total_following': int,
            'total_followers': int,
            'total_todos': int,
            'total_credit_received': int,
            'total_credit_given': int
        }
    }
    
    def __init__(self, setup=False):
        AUserDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addUser(self, user):
#         self.addUsers([user])
        return self._collection.insert(self._userToBSON(user))
    
    def getUser(self, userID):
        user = User(self._collection.find_one(userID))
        if user.isValid == False:
            raise KeyError("User not valid")
        return user
        
    def updateUser(self, user):
        return self._collection.save(self._userToBSON(user))
        
    def removeUser(self, user):
        return self._collection.remove(self._userToBSON(user))
    
    def addUsers(self, users):
        userData = []
        for user in users:
            userData.append(self._userToBSON(user))
        return self._collection.insert(userData)

    
    ### PRIVATE
    
    def _userToBSON(self, user):
        if user.isValid == False:
            raise KeyError("User not valid")
        data = user.getDataAsDict()
        return self._mapDataToSchema(data, self.SCHEMA)
        
        
        
#         
#         
# 
# 
#     # Denotes relationship between object and SQL table structure -- primary
#     # use is to map fields between both structures.
#     # First item in tuple is OBJECT ATTRIBUTE, second is COLUMN NAME.
#     MAPPING = [
#             ('id', 'user_id'),
#             ('email', 'email'),
#             ('username', 'username'),
#             ('name', 'name'),
#             ('password', 'password'),
#             ('bio', 'bio'),
#             ('website', 'website'),
#             ('image', 'image'),
#             ('privacy', 'privacy'),
#             ('account', 'account'),
#             ('flagged', 'flagged'),
#             ('locale', 'locale'),
#             ('timezone', 'timezone')
#         ]
#     
#     def __init__(self, setup=False):
#         AUserDB.__init__(self, self.DESC)
#         MySQL.__init__(self, mapping=self.MAPPING)
#         
#         self.db = self._getConnection()
#         self._lock = Lock()
#         if setup:
#             self._createUserTable()
#         
#     ### PUBLIC
#     
#     def addUser(self, user):
#         user = self._mapObjToSQL(user)
#         
#         def _addUser(cursor):
#             query = """INSERT INTO users 
#                     (email, username, name, privacy) 
#                     VALUES (%(email)s, %(username)s, %(name)s, %(privacy)s)"""
#             cursor.execute(query, user)
#             return cursor.lastrowid
# 
#         return self._transact(_addUser)
#     
#     def getUser(self, userID):
#         userID = int(userID)
#         
#         def _getUser(cursor):
#             query = "SELECT * FROM users WHERE user_id = %d" % (userID)
#             cursor.execute(query)
#             
#             if cursor.rowcount > 0:
#                 data = cursor.fetchone()
#                 user = User()
#                 return self._mapSQLToObj(data, user)
#             else:
#                 return None
#         
#         return self._transact(_getUser, returnDict=True)
#     
#     def updateUser(self, user):
#         user = self._mapObjToSQL(user)
#         user['date_updated'] = datetime.now().isoformat()
#                 
#         def _updateUser(cursor):
#             query = """UPDATE users SET 
#                        email = %(email)s, 
#                        username = %(username)s, 
#                        name = %(name)s, 
#                        privacy = %(privacy)s 
#                        WHERE user_id = %(user_id)s"""
#             cursor.execute(query, user)
#             
#             return (cursor.rowcount > 0)
#         
#         return self._transact(_updateUser)
#       
#     def removeUser(self, userID):
#         def _removeUser(cursor):
#             query = "DELETE FROM users WHERE user_id = %s" % (userID)
#             cursor.execute(query)
#             
#             return (cursor.rowcount > 0)
#         
#         return self._transact(_removeUser)
#         
#     def lookupUsers(self, userIDs, usernames):
#         
#         def _lookupUsers(cursor):
#             if userIDs:                
#                 format_strings = ','.join(['%s'] * len(userIDs))
#                 cursor.execute("SELECT * FROM users WHERE user_id IN (%s)" % 
#                     format_strings, tuple(userIDs))
#             elif usernames:                
#                 format_strings = ','.join(['%s'] * len(usernames))
#                 cursor.execute("SELECT * FROM users WHERE username IN (%s)" % 
#                     format_strings, tuple(usernames))
#             else:
#                 return None
#                     
#             usersData = cursor.fetchall()
#             
#             users = []
#             for userData in usersData:
#                 user = User()
#                 user = self._mapSQLToObj(userData, user)
#                 users.append(user)
#                 
#             return users
#         
#         return self._transact(_lookupUsers, returnDict=True)
#         
#     def searchUsers(self, searchQuery):
#         
#         def _searchUsers(cursor):
#             query = ("""SELECT user_id, email, username, name, image, privacy,
#                     MATCH (username, name, email) AGAINST ('%s') AS score
#                     FROM users
#                     ORDER BY score DESC
#                     LIMIT 0, 10""" %
#                     (searchQuery))
#                     
#             cursor.execute(query)
#             usersData = cursor.fetchall()
#             
#             users = []
#             for userData in usersData:
#                 user = User()
#                 user = self._mapSQLToObj(userData, user)
#                 users.append(user)
#                 
#             return users
#         
#         return self._transact(_searchUsers, returnDict=True)
#             
#     ### PRIVATE
#     
#     def _createUserTable(self):
#         def _createTable(cursor):
#             query = """CREATE TABLE users (
#                     user_id INT NOT NULL AUTO_INCREMENT, 
#                     email VARCHAR(100), 
#                     username VARCHAR(20), 
#                     name VARCHAR(50), 
#                     password VARCHAR(20), 
#                     bio TEXT, 
#                     website VARCHAR(250),
#                     image VARCHAR(100),
#                     privacy INT, 
#                     account VARCHAR(100),
#                     flagged INT,
#                     locale VARCHAR(100),
#                     timezone VARCHAR(10),
#                     PRIMARY KEY(user_id))
#                     ENGINE = MyISAM"""
#             cursor.execute(query)
#             cursor.execute("CREATE INDEX ix_email ON users (email)")
#             
#             ## TODO: Remove fulltext index and switch the table back to using InnoDB
#             cursor.execute("ALTER TABLE users ADD FULLTEXT(username, name, email)")
#             
#             return True
#             
#         return self._transact(_createTable)
        