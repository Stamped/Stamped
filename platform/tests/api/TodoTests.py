#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from AStampedAPITestCase import *

# ##### #
# TODOS #
# ##### #

class StampedAPITodoTest(AStampedAPITestCase):
    def setUp(self):
        (self.userA, self.tokenA) = self.createAccount('UserA')
        (self.userB, self.tokenB) = self.createAccount('UserB')
        self.entity = self.createEntity(self.tokenA)
        self.stamp = self.createStamp(self.tokenA, self.entity['entity_id'])
        self.todo = self.createTodo(self.tokenB,\
            self.entity['entity_id'])

    def tearDown(self):
        self.deleteTodo(self.tokenB, self.entity['entity_id'])
        self.deleteStamp(self.tokenA, self.stamp['stamp_id'])
        self.deleteEntity(self.tokenA, self.entity['entity_id'])
        self.deleteAccount(self.tokenA)
        self.deleteAccount(self.tokenB)

class StampedAPITodosShow(StampedAPITodoTest):
    def test_show(self):
        path = "todos/show.json"
        data = {
            "oauth_token": self.tokenB['access_token'],
            }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

    def test_show_nothing(self):
        path = "todos/show.json"
        data = {
            "oauth_token": self.tokenA['access_token'],
            }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 0)

class StampedAPITodosAlreadyComplete(StampedAPITodoTest):
    def test_create_completed(self):
        self.entityB    = self.createEntity(self.tokenB)
        self.stampB     = self.createStamp(self.tokenB, self.entityB['entity_id'])
        self.todoB      = self.createTodo(self.tokenB, self.entityB['entity_id'])

        path = "todos/show.json"
        data = {
            "oauth_token": self.tokenB['access_token'],
            }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 2)

        from pprint import pformat
        print(pformat(result))
        if result[0]['source']['entity']['entity_id'] == self.entityB['entity_id']:
            self.assertTrue(result[0]['complete'])
        else:
            self.assertTrue(result[1]['complete'])

        self.deleteTodo(self.tokenB, self.entityB['entity_id'])
        self.deleteStamp(self.tokenB, self.stampB['stamp_id'])
        self.deleteEntity(self.tokenB, self.entityB['entity_id'])

class StampedAPITodosAlreadyOnList(StampedAPITodoTest):
    def test_already_on_list(self):
        with expected_exception():
            self.todoB = self.createTodo(self.tokenB, self.entity['entity_id'])

class StampedAPITodosViaStamp(StampedAPITodoTest):
    def test_show_via_stamp(self):
        self.deleteTodo(self.tokenB, self.entity['entity_id'])
        self.todo = self.createTodo(self.tokenB,\
            self.entity['entity_id'],\
            stampId=self.stamp['stamp_id'])

        path = "todos/show.json"
        data = {
            "oauth_token": self.tokenB['access_token'],
            }
        result = self.handleGET(path, data)
        self.assertEqual(len(result), 1)

if __name__ == '__main__':
    main()

