# CP2_BucketList
[![Build Status](https://travis-ci.org/cnagadya/CP2_BucketList.svg?branch=develop)](https://travis-ci.org/cnagadya/CP2_BucketList)
[![Coverage Status](https://coveralls.io/repos/github/cnagadya/CP2_BucketList/badge.svg?branch=develop)](https://coveralls.io/github/cnagadya/CP2_BucketList?branch=develop)

> A REST API for an online bucketlist service

###### API Endpoints
| EndPoint                                | Functionality                     |
|-----------------------------------------|-----------------------------------|
| POST /auth/login                        | Logs a user in                    |
| POST /auth/register                     | Register a user                   |
| POST /bucketlists/                      | Create a new bucket list          |
| GET /bucketlists/                       | List all the created bucket lists |
| GET /bucketlists/`id`                   | Get single bucket list            |
| PUT /bucketlists/`id`                   | Update this bucket list           |
| DELETE /bucketlists/`id`                | Delete this single bucket list    |
| POST /bucketlists/`id`/items/           | Create a new item in bucket list  |
| PUT /bucketlists/`id`/items/`item_id`   | Update a bucket list item         |
| DELETE /bucketlists/`id`items/`item_id` | Delete an item in a bucket list   |

###### User Guide
1. Clone or download this repository to a computer that has python installed. Else download python [here](https://www.python.org/downloads/)
2. Install pip and virtual environment using the commands below, one after the other
```
easy_install pip
```
```
pip install virtualenv
```

3. Navigate to the application folder
4. Create a virtual environment for the project in the root folder using the command:
```
virtualenv venv
```
5. Activate the virtual environment using the command:
```
source venv/bin/activate
```
6. Install all the application dependencies listed in the requirements.txt file using the command:
```
pip install -r requirements.txt
```
7. And then executing the app.py file using:
```
python run.py
```
