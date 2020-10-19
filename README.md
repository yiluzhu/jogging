A REST API that tracks jogging details
=============================================

Introduction
------------
This API is able to manage user accounts as well as jogging details for each user.

Some important features are:

  * There are three roles with different permission levels:
    * a regular user would only be able to CRUD on their owned records.
    * a staff would be able to CRUD only users.
    * an admin would be able to CRUD all records and users.

  * A jogging record has a date, distance, time, and location.
    Based on the provided date and location, the weather conditions would be added automatically. \
    Note: History only support up to 5 days at the moment.

  * The API creates a report on average speed & distance per week.

  * The API provides filter capabilities for endpoints that return a list, and support pagination. Filtering allow using parenthesis. \
    Example -> (date eq '2016-05-01') and ((distance gt 20) or (distance lt 10)).

  * All user and admin actions can be performed via the API, including authentication.

All the code can be found in: https://git.toptal.com/screening/yilu-zhu


Prerequisite
------------
Python 3.6 and above. \
For production in Linux gunicorn is required.


How to start the app
--------------------
For development
```
  python app.py
```
For production in Linux (running on port 8080 with 8 processes)
```
  gunicorn -b 0.0.0.0:8080 workers=8 app:app
```
