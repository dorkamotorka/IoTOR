#!/usr/bin/env python3

import unittest
from requests import Session
import random
import string

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def assert_in_response_message(response, message: str):
    assert message.lower() in response.json()["message"].lower()

def assert_is_success(response):
    assert response.status_code == 200
    return response.json()["success"] == True

def assert_is_fail(response):
    assert response.status_code == 500
    return response.json()["success"] == False


# tests

class TestAPI(unittest.TestCase):

    BASE = "http://localhost:5000"
    s = Session()

    def setUp(self):
        self.BASE = __class__.BASE
        self.s = __class__.s
        self.n = 3

    def test_0_register_nodes(self):
        for _ in range(self.n): 
            r = get_random_string(6) 
            VALID_NODE_JSON = {"name": f"name_{r}", "kind": "entry", "address": f"host_{r}", "public_key": f"key_{r}"}
            response = self.s.post(self.BASE + "/admin/node", json=VALID_NODE_JSON)
            assert_is_success(response)

    def test_1_invalid_duplicate(self):
        r = get_random_string(6) 
        VALID_NODE_JSON = {"name": f"name_{r}", "kind": "entry", "address": f"host_{r}", "public_key": f"key_{r}"}
        response = self.s.post(self.BASE + "/admin/node", json=VALID_NODE_JSON)
        assert_is_success(response)

        # add same name again -> should fail
        response = self.s.post(self.BASE + "/admin/node", json=VALID_NODE_JSON)
        assert_in_response_message(response, "already exists")
        assert_is_fail(response)

        resp = self.s.get(self.BASE + '/node?num_nodes=-1')
        count = 0
        for node in resp.json()["data"]:
            if node == VALID_NODE_JSON:
                count += 1
        self.assertEqual(count, 1)

    def test_2_invalid_url(self):
        response = self.s.get(self.BASE + '/node/invalid')
        assert response.status_code == 404

    def test_3_invalid_node(self):
        resp = self.s.get(self.BASE + '/node?num_nodes=-1')
        before = len(resp.json()["data"])

        # insert invalid node (additional attribute), make sure node list is still empty
        INVALID_NODE_JSON = {"name": "name1", "kind": "entry", "address": "host1", "public_key": "key1", "INVALID": "A"}
        response = self.s.post(self.BASE + "/admin/node", json=INVALID_NODE_JSON)
        assert_is_fail(response)
        assert_in_response_message(response, "unknown field")

        resp = self.s.get(self.BASE + '/node?num_nodes=-1')
        after = len(resp.json()["data"])
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
