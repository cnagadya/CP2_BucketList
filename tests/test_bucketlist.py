import unittest
import json
import os
from datetime import datetime
import time
from app.bucketlist_api_v1 import bucketlists, items, session_management
from app import create_app, db
from app.models import User


class BucketlistTestcase(unittest.TestCase):
    def setUp(self):
        self.app, self.db = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            # create all tables
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    def create_user(self):
        self.data = {"username": "Christine",
                     "email_add": "email@axample.com", "password": "1234"}
        response = self.client.post("/api/v1/auth/register", data=json.dumps(
            self.data), headers={"content-type": "application/json"})
        return response

    def login_user(self):
        response = self.create_user()
        logged_in = self.client.post("/api/v1/auth/login", data=json.dumps(
            {"username": "Christine", "password": "1234"}), headers={"content-type": "application/json"})
        token = json.loads(logged_in.data)['Generated Token']
        return token

    def login_other_user(self):
        self.other_data = {"username": "Andela",
                           "email_add": "abc@axample.com", "password": "1234"}
        response1 = self.client.post("/api/v1/auth/register", data=json.dumps(
            self.other_data), headers={"content-type": "application/json"})
        self.assertEqual(response1.status_code, 201)
        new_login = self.client.post("/api/v1/auth/login", data=json.dumps(
            {"username": "Andela", "password": "1234"}), headers={"content-type": "application/json"})
        new_token = json.loads(new_login.data)['Generated Token']
        return new_token

    def test_create_account(self):
        response = self.create_user()
        result = json.loads(response.data)
        self.assertEqual(
            [{'username': 'Christine', 'email address': 'email@axample.com'}], result["Successful Added"])
        self.assertEqual(response.status_code, 201)

    def test_create_account_invalid_email(self):
        self.data = {"username": "Christine",
                     "email_add": "email@axamplecom", "password": "1234"}
        response = self.client.post("/api/v1/auth/register", data=json.dumps(
            self.data), headers={"content-type": "application/json"})
        result = json.loads(response.data)
        self.assertEqual(
            "Email address should have 'email@example.com' format", result["message"])
        self.assertEqual(response.status_code, 400)

    def test_create_account_missing_parameters(self):
        self.data = {"username": "Christine",  "password": "1234"}
        response = self.client.post("/api/v1/auth/register", data=json.dumps(
            self.data), headers={"content-type": "application/json"})
        result = json.loads(response.data)
        self.assertEqual(
            "Enter the username, email address and password to create account", result["message"])
        self.assertEqual(response.status_code, 400)

    def test_register_username_exists(self):
        response = self.create_user()
        self.assertEqual(response.status_code, 201)
        response2 = self.create_user()
        result = json.loads(response2.data)
        self.assertEqual(
            "User with username 'Christine' already exists", result["message"])

    def test_register_username_is_digit(self):
        self.data = {"username": "1234",
                     "email_add": "email@axample.com", "password": "1234"}
        response = self.client.post("/api/v1/auth/register", data=json.dumps(
            self.data), headers={"content-type": "application/json"})
        result = json.loads(response.data)
        self.assertEqual("Invalid value entered for username and / or password",
                         result["message"])

    def test_login(self):
        response = self.create_user()
        login_response = self.client.post("/api/v1/auth/login", data=json.dumps(
            {"username": "Christine", "password": "1234"}), headers={"content-type": "application/json"})
        self.assertEqual(login_response.status_code, 200)
        result = json.loads(login_response.data)
        self.assertIn('Generated Token', result.keys())

    def test_login_invalid_credentials(self):
        login_response = self.client.post("/api/v1/auth/login", data=json.dumps(
            {"username": "andela", "password": "12345"}), headers={"content-type": "application/json"})
        self.assertEqual(login_response.status_code, 409)
        result = json.loads(login_response.data)
        self.assertEqual("Invalid username or password", result['message'])

    def test_login_missing_credentials(self):
        login_response = self.client.post("/api/v1/auth/login", data=json.dumps(
            {"username": "andela"}), headers={"content-type": "application/json"})
        self.assertEqual(login_response.status_code, 400)
        result = json.loads(login_response.data)
        self.assertEqual("Enter the username and password", result['message'])

    def test_add_bucketlist(self):
        token = self.login_user()
        response = self.client.post("/api/v1/bucketlists", data=json.dumps(
            {"name": "Hawaiiiii"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(response.status_code, 201)
        result = json.loads(response.data)
        self.assertIn("Hawaiiiii", str(result))

    def test_view_bucketlists_with_invalid_token(self):
        response = self.client.get("/api/v1/bucketlists/", headers={
                                   "content-type": "application/json", "Authorization": "Bearer abcd"})
        self.assertEqual(response.status_code, 401)
        result = json.loads(response.data)
        self.assertEqual(
            "Enter a valid authentication token code", result['message'])

    def test_view_all_bucketlists(self):
        token = self.login_user()
        add_response = self.client.post("/api/v1/bucketlists", data=json.dumps(
            {"name": "Visit every country in the world"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_response.status_code, 201)
        response = self.client.get("/api/v1/bucketlists", headers={
                                   "content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn("Visit every country in the world", str(result))

    def test_view_all_bucketlists_none_added(self):
        token = self.login_user()
        response = self.client.get("/api/v1/bucketlists", headers={
                                   "content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(
            "You have not added any bucketlist yet", result["message"])

    def test_view_bucketlist_no_items_added(self):
        token = self.login_user()
        add_response = self.client.post("/api/v1/bucketlists", data=json.dumps(
            {"name": "Visit every country in the world"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_response.status_code, 201)
        response = self.client.get("/api/v1/bucketlists/1", headers={
                                   "content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn(
            "Visit every country in the world has no items", str(result))

    def test_view_single_bucketlist(self):
        token = self.login_user()
        add_response = self.client.post("/api/v1/bucketlists", data=json.dumps(
            {"name": "Swim in the ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_response.status_code, 201)
        response = self.client.get("/api/v1/bucketlists/1", headers={
                                   "content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn("Swim in the ocean", str(result))
        self.assertIn("Bucketlist Items", str(result))

    def test_view_bucketlist_no_access(self):
        token = self.login_user()
        add_response = self.client.post("/api/v1/bucketlists", data=json.dumps(
            {"name": "Swim in the ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_response.status_code, 201)
        new_token = self.login_other_user()
        response = self.client.get("/api/v1/bucketlists/1", headers={
                                   "content-type": "application/json", "Authorization": "Bearer " + new_token})
        self.assertEqual(response.status_code, 401)
        result = json.loads(response.data)
        self.assertEqual(
            "You are not authorised to view this bucketlist!", result['message'])

    def test_view_bucketlist_invalid_id(self):
        token = self.login_user()
        response = self.client.get("/api/v1/bucketlists/1", headers={
                                   "content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(response.status_code, 404)
        result = json.loads(response.data)
        self.assertEqual("Invalid resource URI", result['message'])

    def test_edit_bucketlist(self):
        token = self.login_user()
        add_response = self.client.post("/api/v1/bucketlists", data=json.dumps(
            {"name": "Swim in the ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_response.status_code, 201)
        edit_response = self.client.put("/api/v1/bucketlists/1", data=json.dumps(
            {"name": "Swim in the Indian ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(edit_response.status_code, 202)
        result = json.loads(edit_response.data)
        self.assertIn("Swim in the Indian ocean", str(result))

    def test_edit_bucketlist_no_access(self):
        token = self.login_user()
        add_response = self.client.post("/api/v1/bucketlists", data=json.dumps(
            {"name": "Swim in the ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_response.status_code, 201)
        new_token = self.login_other_user()
        edit_response = self.client.put("/api/v1/bucketlists/1", data=json.dumps(
            {"name": "Swim in the Indian ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + new_token})
        self.assertEqual(edit_response.status_code, 401)
        result = json.loads(edit_response.data)
        self.assertEqual(
            "You are not authorised to modify this bucketlist!", result['message'])

    def test_edit_bucketlist_invalid_id(self):
        token = self.login_user()
        edit_response = self.client.put("/api/v1/bucketlists/1", data=json.dumps(
            {"name": "Swim in the Indian ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(edit_response.status_code, 404)
        result = json.loads(edit_response.data)
        self.assertEqual("Invalid resource URI", result['message'])

    def test_delete_bucketlist(self):
        token = self.login_user()
        add_response = self.client.post("/api/v1/bucketlists", data=json.dumps(
            {"name": "Swim in the oceans"}),headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_response.status_code, 201)
        del_response = self.client.delete("/api/v1/bucketlists/1", headers={
                                          "content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(del_response.status_code, 410)
        result = json.loads(del_response.data)
        self.assertIn("Bucketlist successfully deleted", str(result))

    def test_delete_bucketlist_no_access(self):
        token = self.login_user()
        add_response = self.client.post("/api/v1/bucketlists",data=json.dumps(
            {"name": "Swim in the oceans"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_response.status_code, 201)
        new_token = self.login_other_user()
        del_response = self.client.delete("/api/v1/bucketlists/1", headers={
                                          "content-type": "application/json", "Authorization": "Bearer " + new_token})
        self.assertEqual(del_response.status_code, 401)
        result = json.loads(del_response.data)
        self.assertEqual(
            "You are not authorised to delete this bucketlist!", result['message'])

    def test_delete_bucketlist_invalid_id(self):
        token = self.login_user()
        del_response = self.client.delete("/api/v1/bucketlists/1",data=json.dumps(
            {"name": "Swim in the oceans"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(del_response.status_code, 404)
        result = json.loads(del_response.data)
        self.assertEqual("Invalid resource URI", result['message'])

    def test_add_item_to_bucket(self):
        token = self.login_user()
        add_response = self.client.post("/api/v1/bucketlists", data=json.dumps(
            {"name": "Swim in the oceans"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_response.status_code, 201)
        add_item_response = self.client.post("/api/v1/bucketlists/1/items", data=json.dumps(
            {"name": "Indian ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_item_response.status_code, 201)
        result = json.loads(add_item_response.data)
        self.assertIn("Successfully Added item with details", str(result))

    def test_add_item_to_bucket_no_access(self):
        token = self.login_user()
        add_response = self.client.post("/api/v1/bucketlists",  data=json.dumps({"name": "Swim in the ocean"}), headers={
                                        "content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_response.status_code, 201)
        new_token = self.login_other_user()
        add_item_response = self.client.post("/api/v1/bucketlists/1/items", data=json.dumps(
            {"name": "Indian ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + new_token})
        self.assertEqual(add_item_response.status_code, 401)
        result = json.loads(add_item_response.data)
        self.assertEqual(
            "You have no access to this bucketlist", result['message'])

    def test_add_item_to_bucket_invalid_id(self):
        token = self.login_user()
        add_item_response = self.client.post("/api/v1/bucketlists/1/items", data=json.dumps(
            {"name": "Indian ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_item_response.status_code, 404)
        result = json.loads(add_item_response.data)
        self.assertIn("Invalid resource URI", str(result))

    def test_edit_item_in_bucket(self):
        token = self.login_user()
        add_response = self.client.post("/api/v1/bucketlists", data=json.dumps(
            {"name": "Swim in the oceans"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_response.status_code, 201)
        add_item_response = self.client.post("/api/v1/bucketlists/1/items", data=json.dumps(
            {"name": "Indian ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_item_response.status_code, 201)
        edit_item_response = self.client.put("/api/v1/bucketlists/1/items/1", data=json.dumps(
            {"name": "The Indian Ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        result = json.loads(edit_item_response.data)
        self.assertIn("The Indian Ocean", str(result))

    def test_edit_item_in_bucket_no_access(self):
        token = self.login_user()
        add_response = self.client.post("/api/v1/bucketlists",  data=json.dumps({"name": "Swim in the ocean"}), headers={
                                        "content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_response.status_code, 201)

        add_item_response = self.client.post("/api/v1/bucketlists/1/items", data=json.dumps(
            {"name": "Indian ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_item_response.status_code, 201)
        new_token = self.login_other_user()
        edit_item_response = self.client.put("/api/v1/bucketlists/1/items/1", data=json.dumps(
            {"name": "The Indian Ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + new_token})
        self.assertEqual(edit_item_response.status_code, 401)
        result = json.loads(edit_item_response.data)
        self.assertEqual(
            "You have no access to this bucketlist", result['message'])

    def test_remove_item_from_bucket(self):
        token = self.login_user()
        add_response = self.client.post("/api/v1/bucketlists", data=json.dumps(
            {"name": "Swim in the oceans"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_response.status_code, 201)
        add_item_response = self.client.post("/api/v1/bucketlists/1/items", data=json.dumps(
            {"name": "Indian ocean"}), headers={"content-type": "application/json", "Authorization": "Bearer " + token})
        self.assertEqual(add_item_response.status_code, 201)
        del_item_response = self.client.delete("/api/v1/bucketlists/1/items/1",  headers={
                                               "content-type": "application/json", "Authorization": "Bearer " + token})
        result = json.loads(del_item_response.data)
        self.assertIn(
            "Item successfully deleted from Swim in the oceans", str(result))
