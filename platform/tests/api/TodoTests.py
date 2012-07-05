#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPIHttpTestCase import *

# ##### #
# TODOS #
# ##### #

class StampedAPITodoHttpTest(AStampedAPIHttpTestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.entity = self.createEntity(self.tokenA)
        self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'])
        self.todo = self.createTodo(self.tokenB, self.entity['entity_id'], self.stamp['stamp_id'])

    def tearDown(self):
        self.deleteTodo(self.tokenB, self.entity['entity_id'])
        self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
        self.deleteEntity(self.tokenA, self.entity['entity_id'])
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPITodosShow(StampedAPITodoHttpTest):
    def test_show(self):
        path = "todos/collection.json"
        data = {
            "oauth_token": self.tokenB['access_token'],
            }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

    def test_show_nothing(self):
        path = "todos/collection.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 0)

class StampedAPITodosComplete(StampedAPITodoHttpTest):
    def test_complete(self):
        todo = self.completeTodo(self.tokenB, self.entity['entity_id'], True)
        path = "todos/collection.json"
        data = {
            "oauth_token": self.tokenB['access_token'],
            }
        result = self.handleGET(path, data)
        self.assertEqual(result[0]['complete'], True)

    def test_uncomplete(self):
        todo = self.completeTodo(self.tokenB, self.entity['entity_id'], False)
        path = "todos/collection.json"
        data = {
            "oauth_token": self.tokenB['access_token'],
            }
        result = self.handleGET(path, data)
        self.assertEqual(result[0]['complete'], False)

class StampedAPITodosPreviews(StampedAPITodoHttpTest):
    def test_previews_friends(self):
        # Create User C and User D, who also todo the tntity.  User B should see both users in the preview
        (self.userC, self.tokenC) = self.createAccount('UserC')
        (self.userD, self.tokenD) = self.createAccount('UserD')
        self.createFriendship(self.tokenC, self.userB)
        self.createFriendship(self.tokenD, self.userB)
        self.todo = self.createTodo(self.tokenC, self.entity['entity_id'])
        self.todo = self.createTodo(self.tokenD, self.entity['entity_id'])

        path = "todos/collection.json"
        data = {
            "oauth_token": self.tokenB['access_token'],
            }
        result = self.handleGET(path, data)

        self.assertEqual(len(result[0]['previews']['todos']), 2)
        self.assertEqual(len(result[0]['previews']['stamps']), 1)
        self.assertEqual(result[0]['previews']['stamps'][0]['stamp_id'], self.stamp['stamp_id'])
        self.assertEqual(result[0]['previews']['stamps'][0]['user']['user_id'], self.userA['user_id'])

        self.deleteTodo(self.tokenD, self.entity['entity_id'])
        self.deleteTodo(self.tokenC, self.entity['entity_id'])
        self.deleteAccount(self.tokenD)
        self.deleteAccount(self.tokenC)

class StampedAPITodosAlreadyComplete(StampedAPITodoHttpTest):
    def test_create_completed(self):
        self.entityB    = self.createEntity(self.tokenB)
        self.stampB     = self.createStamp(self.tokenB, self.entityB['entity_id'])
        self.todoB      = self.createTodo(self.tokenB, self.entityB['entity_id'])

        path = "todos/collection.json"
        data = {
            "oauth_token": self.tokenB['access_token'],
            }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 2)

        if result[0]['source']['entity']['entity_id'] == self.entityB['entity_id']:
            self.assertTrue(result[0]['complete'])
        else:
            self.assertTrue(result[1]['complete'])

        self.deleteTodo(self.tokenB, self.entityB['entity_id'])
        self.deleteStamp(self.tokenB, self.stampB['stamp_id'])
        self.deleteEntity(self.tokenB, self.entityB['entity_id'])

class StampedAPITodosAlreadyOnList(StampedAPITodoHttpTest):
    def test_already_on_list(self):
        todo = self.createTodo(self.tokenB, self.entity['entity_id'])
        self.assertTrue(self.todo['todo_id'] == todo['todo_id'])

class StampedAPITodosViaStamp(StampedAPITodoHttpTest):
    def test_show_via_stamp(self):
        self.deleteTodo(self.tokenB, self.entity['entity_id'])
        self.todo = self.createTodo(self.tokenB,\
            self.entity['entity_id'],\
            stampId=self.stamp['stamp_id'])

        path = "todos/collection.json"
        data = {
            "oauth_token": self.tokenB['access_token'],
            }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

    def test_todo_own_stamp(self):
        self.todo = self.createTodo(self.tokenA, self.entity['entity_id'], stampId=self.stamp['stamp_id'])

        path = "todos/collection.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

if __name__ == '__main__':
    main()

