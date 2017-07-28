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
        self.assertEqual("Username can not have just numbers",
                         result["message"])

    def test_login(self):
        response = self.create_user()
        login_response = self.client.post("/api/v1/auth/login", data=json.dumps(
            {"username": "Christine", "password": "1234"}), headers={"content-type": "application/json"})
        self.assertEqual(login_response.status_code, 201)
        result = json.loads(login_response.data)
        self.assertIn('Generated Token', result.keys())

    def test_login_invalid_credentials(self):
        login_response = self.client.post("/api/v1/auth/login", data=json.dumps(
            {"username": "andela", "password": "12345"}), headers={"content-type": "application/json"})
        self.assertEqual(login_response.status_code, 403)
        result = json.loads(login_response.data)
        self.assertEqual("Invalid username or password", result['message'])

    def test_login_missing_credentials(self):
        login_response = self.client.post("/api/v1/auth/login", data=json.dumps(
            {"username": "andela"}), headers={"content-type": "application/json"})
        self.assertEqual(login_response.status_code, 400)
        result = json.loads(login_response.data)
        self.assertEqual("Enter the username and password", result['message'])
