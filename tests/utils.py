import uuid
import random
import datetime
import hashlib
import names
from services.db import dbs


ADMIN_TOKEN = '1cd7e93b-3311-48e3-be60-fd4b92a64eab'


def create_random_users(num):
    usernames = []
    for i in range(num):
        name = names.get_full_name()
        forename, surname = name.split()
        username = name.lower().replace(' ', '')
        password = hashlib.sha1('aaa'.encode()).hexdigest()
        email = f'{forename}.{surname}@gmail.com'.lower()
        dbs.create_a_user({'forename': forename, 'surname': surname, 'username': username,
                          'password': password, 'email': email, 'role': 'user'}, ADMIN_TOKEN)
        usernames.append(username)

    return usernames


def create_admin_user(params=None):
    params = params or {
        'forename': 'Yilu', 'surname': 'Zhu', 'username': 'yiluzhu',
        'password': hashlib.sha1('qwe123'.encode()).hexdigest(), 'email': '', 'role': 'admin', 'token': ADMIN_TOKEN
    }
    dbs.create_admin_user(params)


def create_random_records(usernames, num):
    for i in range(num):
        params = {'username': random.choice(usernames), 'date': datetime.date(2020, 9, random.randint(26, 29)),
                  'lat': random.randint(-700, 700) / 10, 'lon': random.randint(-1790, 1790) / 10,
                  'distance': random.randint(1000, 10000), 'time': random.randint(5, 60)}
        dbs.create_a_record(params, ADMIN_TOKEN)


def create_test_db(user_num, record_num):
    create_admin_user()
    usernames = create_random_users(user_num)
    create_random_records(usernames, record_num)


def create_user_table_from_df(df, token):
    for row in df.to_dict('records'):
        if row['role'] == 'admin':
            dbs.create_admin_user(row)
        else:
            dbs.create_a_user(row, token)


def create_record_table_from_df(df, token):
    for row in df.to_dict('records'):
        dbs.create_a_record(row, token)


if __name__ == '__main__':
    # create_admin_user()
    # print('admin token', ADMIN_TOKEN)
    create_random_users(20)
