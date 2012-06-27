#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPIHttpTestCase import *

# ######## #
# COMMENTS #
# ######## #

class StampedAPICommentHttpTest(AStampedAPIHttpTestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.createFriendship(self.tokenB, self.userA)
        self.entity = self.createEntity(self.tokenA)
        self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'])
        self.blurbA = "Great place"
        self.blurbB = "Glad you liked it!"
        self.commentA = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurbA)
        self.commentB = self.createComment(self.tokenA, self.stamp['stamp_id'], \
            self.blurbB)

    def tearDown(self):
        self.deleteComment(self.tokenA, self.commentB['comment_id'])
        self.deleteComment(self.tokenB, self.commentA['comment_id'])
        self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
        self.deleteEntity(self.tokenA, self.entity['entity_id'])
        self.deleteFriendship(self.tokenB, self.userA)
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPICommentsShow(StampedAPICommentHttpTest):
    def test_show(self):
        path = "comments/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertIn(result[0]['blurb'],[self.blurbA, self.blurbB])
        self.assertIn(result[1]['blurb'],[self.blurbA, self.blurbB])

class StampedAPICommentsRemovePermissions(StampedAPICommentHttpTest):
    def test_remove_fail(self):
        path = "comments/remove.json"
        data = { 
            "oauth_token": self.tokenB['access_token'],
            "comment_id": self.commentB['comment_id']
        }
        
        with expected_exception():
            result = self.handlePOST(path, data)

class StampedAPICommentsRemoveStampOwner(StampedAPICommentHttpTest):
    def test_show(self):
        path = "comments/remove.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "comment_id": self.commentA['comment_id']
        }
        result = self.handlePOST(path, data)

        # Add it back or else the test will fail...!
        self.commentA = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurbA)

class StampedAPICommentsMentions(StampedAPICommentHttpTest):
    def test_mention(self):
        self.blurb = "Nice job @%s!" % self.userA['screen_name']
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(len(result[0]['blurb_references']) == 1)
        self.assertTrue(result[0]['blurb_references'][0]['indices'] == [9, 15])

        self.deleteComment(self.tokenB, self.comment['comment_id'])

    def test_double_mention(self):
        self.blurb = "Nice job @%s! You rock @%s." % \
            (self.userA['screen_name'], self.userB['screen_name'])
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(len(result[0]['blurb_references']) == 2)

        self.deleteComment(self.tokenB, self.comment['comment_id'])

class StampedAPICommentsReply(StampedAPICommentHttpTest):
    def test_reply(self):
        self.blurb = "@%s thanks!" % self.userA['screen_name']
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(len(result[0]['blurb_references']) == 1)

        self.deleteComment(self.tokenB, self.comment['comment_id'])

    def test_reply_upper(self):
        self.blurb = "@%s thanks!" % str(self.userA['screen_name']).upper()
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(len(result[0]['blurb_references']) == 1)

        self.deleteComment(self.tokenB, self.comment['comment_id'])

    def test_reply_lower(self):
        self.blurb = "@%s thanks!" % str(self.userA['screen_name']).lower()
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/collection.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(len(result[0]['blurb_references']) == 1)

        self.deleteComment(self.tokenB, self.comment['comment_id'])

    def test_reply_empty(self):
        self.blurb = "@ thanks!"
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue('blurb_references' not in result[0] or len(result[0]['blurb_references']) == 0)

        self.deleteComment(self.tokenB, self.comment['comment_id'])

    def test_reply_email(self):
        self.blurb = "kevin@stamped.com thanks!"
        self.comment = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            self.blurb)

        path = "comments/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue('blurb_references' not in result[0] or len(result[0]['blurb_references']) == 0)

        self.deleteComment(self.tokenB, self.comment['comment_id'])

class StampedAPICommentsText(StampedAPICommentHttpTest):
    def test_utf8(self):
        blurb = '“Iñtërnâtiônàlizætiøn”'
        commentUTF = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            blurb)

        path = "comments/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(result[0]['blurb'] == blurb.decode('utf-8'))

        self.deleteComment(self.tokenA, commentUTF['comment_id'])

    def test_doublequotes(self):
        blurb = '"test"'
        commentUTF = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            blurb)

        path = "comments/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(result[0]['blurb'] == blurb.decode('utf-8'))

        self.deleteComment(self.tokenA, commentUTF['comment_id'])

    def test_quotes(self):
        blurb = '\'test\''
        commentUTF = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            blurb)

        path = "comments/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(result[0]['blurb'] == blurb.decode('utf-8'))

        self.deleteComment(self.tokenA, commentUTF['comment_id'])

    def test_other_characters(self):
        blurb = '"test" & \'%test\''
        commentUTF = self.createComment(self.tokenB, self.stamp['stamp_id'], \
            blurb)

        path = "comments/collection.json"
        data = { 
            "oauth_token": self.tokenA['access_token'],
            "stamp_id": self.stamp['stamp_id']
        }
        result = self.handleGET(path, data)
        self.assertTrue(result[0]['blurb'] == blurb.decode('utf-8'))

        self.deleteComment(self.tokenA, commentUTF['comment_id'])

if __name__ == '__main__':
    main()

