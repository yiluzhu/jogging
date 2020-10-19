import os
import uuid
import hashlib
import datetime
from loguru import logger
from sqlalchemy.orm import sessionmaker, exc as ormexc
from sqlalchemy import create_engine, exc, event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

from db.models import Base
from db.user import UserTable
from db.jogging import JoggingTable
from services.weather import WeatherAPI
from services.config import DEFAULT_PAGE_NUM, DEFAULT_PAGE_SIZE
from services import exceptions


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """Turn on foreign key constraint in sqlite manually
    """
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


class DBService:
    def __init__(self, db_name, in_memory=False):
        self.db_name = db_name
        self.engine = None
        self.session = self.initialise_db(in_memory)
        self.user_table = UserTable(self.session)
        self.jogging_table = JoggingTable(self.session)
        self.weather_api = WeatherAPI()

    def initialise_db(self, in_memory):
        if in_memory:
            path = ':memory:'
        else:
            path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', self.db_name)

        self.engine = create_engine(f'sqlite:///{path}', connect_args={'check_same_thread': False})
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(self.engine)
        return Session()

    def drop_all_tables(self):
        Base.metadata.drop_all(self.engine)

    def login(self, username, password):
        encrypted_pw = hashlib.sha1(password.encode()).hexdigest()
        try:
            user = self.user_table.get_a_user_by_un_and_pw(username, encrypted_pw)
        except ormexc.NoResultFound:
            msg = 'Wrong username or password'
            logger.error(msg)
            raise exceptions.UnauthenticatedError(msg)

        token = str(uuid.uuid4())
        params = {
            'token': token,
            'username': username,
        }
        self.user_table.update_a_user(params)
        return token

    def logout(self, token):
        try:
            token_owner = self.user_table.get_a_user_by_token(token)
        except ormexc.NoResultFound:
            msg = f'Permission Denied. Unknown token: {token}'
            logger.error(msg)
            raise exceptions.UnauthenticatedError(msg)

        if token_owner:
            self.user_table.update_a_user({
                'username': token_owner.username,
                'token': '',
            })

    def create_a_user(self, params, token):
        """Given some parameters and a token, add a user to user table if the token has permission.

        :param params: parameters for a new user
        :param token: a login token
        :return:
        """
        try:
            token_owner = self.user_table.get_a_user_by_token(token)
        except ormexc.NoResultFound:
            msg = f'Permission Denied. Unknown token: {token}'
            logger.error(msg)
            raise exceptions.UnauthenticatedError(msg)

        if token_owner.role in ['admin', 'staff']:
            if not params.get('username') or not params.get('password'):
                msg = f'Username and password must be provided to create a new user'
                logger.error(msg)
                raise exceptions.MissingInformation(msg)

            params['password'] = hashlib.sha1(params['password'].encode()).hexdigest()
            try:
                self.user_table.create_a_user(params)
            except exc.IntegrityError as e:
                msg = f"User {params['username']} already exists: {e}"
                logger.error(msg)
                raise exceptions.DuplicateUser(msg)
        else:
            msg = f'Permission Denied: {token_owner} can not create new user'
            logger.error(msg)
            raise exceptions.NoAccessError(msg)

    def create_admin_user(self, params):
        """Create admin user
        """
        self.user_table.create_a_user(params)

    def update_a_user(self, params, token):
        """Given some parameters and a token, update the user in user table if the token has permission.

        :param params: new information for a user
        :param token: a login token
        :return:
        """
        try:
            token_owner = self.user_table.get_a_user_by_token(token)
        except ormexc.NoResultFound:
            msg = f'Permission Denied. Unknown token: {token}'
            logger.error(msg)
            raise exceptions.UnauthenticatedError(msg)

        if token_owner.role in ['admin', 'staff']:
            try:
                self.user_table.update_a_user(params)
            except ormexc.NoResultFound:
                msg = f"Failed to update user ({params.get('username')}) who does not exist"
                logger.error(msg)
                raise exceptions.UnknownUser(msg)
        else:
            msg = f'Permission Denied: {token_owner} can not update user'
            logger.error(msg)
            raise exceptions.NoAccessError(msg)

    def delete_a_user(self, username, token):
        """Given a username and a token, delete the user if the token has permission.

        :param username:
            a username in user table

        :param token:
            a login token

        :return:
        """
        try:
            token_owner = self.user_table.get_a_user_by_token(token)
        except ormexc.NoResultFound:
            msg = f'Permission Denied. Unknown token: {token}'
            logger.error(msg)
            raise exceptions.UnauthenticatedError(msg)

        try:
            user = self.user_table.get_a_user_by_username(username)
        except ormexc.NoResultFound:
            msg = f'Failed to delete unknown user: {username}'
            logger.error(msg)
            raise exceptions.UnknownUser(msg)

        if token_owner.role in ['admin', 'staff']:
            try:
                self.user_table.delete_a_user(user)
            except exc.IntegrityError as e:
                msg = f'Can not delete a user that has records: {e}'
                logger.error(msg)
                raise exceptions.UserStillHasRecords(msg)
        else:
            msg = f'Permission Denied: {token_owner} can not delete user {user}'
            logger.error(msg)
            raise exceptions.NoAccessError(msg)

    def read_user_info(self, token, filters, page=DEFAULT_PAGE_NUM, page_size=DEFAULT_PAGE_SIZE):
        """Given a token and a filter dict, return all user information that the token has access to.

        :param token: a login token
        :param filters: a dict of filters
        :param page: page number
        :param page_size: the number of items in each page

        :return: a dict of user information
        """
        try:
            token_owner = self.user_table.get_a_user_by_token(token)
        except ormexc.NoResultFound:
            msg = f'Permission Denied. Unknown token: {token}'
            logger.error(msg)
            raise exceptions.UnauthenticatedError(msg)

        if token_owner.role in ['admin', 'staff']:
            users = self.user_table.get_all_users(filters)
            paged = users[(page - 1) * page_size: page * page_size]
            return [user.to_dict() for user in paged]

        else:
            msg = f'Permission Denied. Token {token} has no access to all users'
            logger.error(msg)
            raise exceptions.NoAccessError(msg)

    def clear_user_table(self):
        self.user_table.clear()

    def create_a_record(self, params, token):
        """Given some parameters and a token, add a record to jogging table if the token has permission.

        :param params: parameters for a new jogging record
        :param token: a login token
        :return:
        """
        try:
            token_owner = self.user_table.get_a_user_by_token(token)
        except ormexc.NoResultFound:
            msg = f'Permission Denied. Unknown token: {token}'
            logger.error(msg)
            raise exceptions.UnauthenticatedError(msg)

        if token_owner.role == 'admin' or token_owner.username == params['username']:
            params['date'] = datetime.datetime.strptime(params['date'], '%Y-%m-%d').date()
            if 'weather' not in params:
                params['weather'] = self.weather_api.get_weather(params['date'], params['lat'], params['lon'])
            try:
                self.jogging_table.create_a_record(params)
            except exc.IntegrityError as e:
                msg = f"Can not create record for unknown user {params['username']}: {e}"
                logger.error(msg)
                raise exceptions.UnknownUser(msg)
        else:
            msg = f'Permission Denied: {token_owner} can not create new record'
            logger.error(msg)
            raise exceptions.NoAccessError(msg)

    def update_a_record(self, params, token):
        """Given some parameters and a token, update a record in jogging table if the token has permission.

        :param params:
            A dict of new information for a record

        :param token:
            A string of login token

        :return:
        """
        try:
            token_owner = self.user_table.get_a_user_by_token(token)
        except ormexc.NoResultFound:
            msg = f'Permission Denied. Unknown token: {token}'
            logger.error(msg)
            raise exceptions.UnauthenticatedError(msg)
        if token_owner.role == 'admin' or token_owner.username == params['username']:
            if params.get('rid'):
                if 'date' in params:
                    params['date'] = datetime.datetime.strptime(params['date'], '%Y-%m-%d').date()
                try:
                    self.jogging_table.update_a_record(params)
                except ormexc.NoResultFound as e:
                    msg = f'Can not update unknown record: {e}'
                    logger.error(msg)
                    raise exceptions.UnknownRecord(msg)
            else:
                msg = 'Update content does not have field "rid"'
                logger.error(msg)
                raise RuntimeError(msg)
        else:
            msg = f'Permission Denied: {token_owner} can not create new record'
            logger.error(msg)
            raise exceptions.NoAccessError(msg)

    def read_records(self, token, filter_dict, page=DEFAULT_PAGE_NUM, page_size=DEFAULT_PAGE_SIZE):
        """Given a token and some filters, return jogging records that the token has access to.

        :param token: a login token
        :param filter_dict: a dict of filters
        :param page: page number
        :param page_size: the number of items in each page

        :return: a dict of jogging records
        """
        try:
            token_owner = self.user_table.get_a_user_by_token(token)
        except ormexc.NoResultFound:
            msg = f'Permission Denied. Unknown token: {token}'
            logger.error(msg)
            raise exceptions.UnauthenticatedError(msg)

        if token_owner.role == 'admin':
            records = self.jogging_table.get_all_records(filter_dict)
        else:
            records = self.jogging_table.get_records_of_a_user(token_owner.username, filter_dict)
        paged = records[(page - 1) * page_size: page * page_size]
        return paged

    def read_all_records_of_a_user(self, token, filter_dict):
        """Given a token and a filter dict, return all records that the token has permission to read.

        :param token: a login token
        :param filter_dict: a dict of filters

        :return: a list of dicts of user information
        """
        try:
            token_owner = self.user_table.get_a_user_by_token(token)
        except ormexc.NoResultFound:
            msg = f'Permission Denied. Unknown token: {token}'
            logger.error(msg)
            raise exceptions.UnauthenticatedError(msg)

        return self.jogging_table.get_records_of_a_user(token_owner.username, filter_dict)

    def delete_a_record(self, rid, token):
        """Given a record id and a token, delete the record if the token has permission.

        :param rid: a record id in jogging table
        :param token: a login token
        :return:
        """
        try:
            token_owner = self.user_table.get_a_user_by_token(token)
        except ormexc.NoResultFound:
            msg = f'Permission Denied. Unknown token: {token}'
            logger.error(msg)
            raise exceptions.UnauthenticatedError(msg)

        try:
            record = self.jogging_table.get_a_record_by_id(rid)
        except ormexc.NoResultFound:
            msg = f'No record found with id: {rid}'
            logger.error(msg)
            raise exceptions.UnknownRecord(msg)

        if token_owner.role == 'admin' or record.username == token_owner.username:
            self.jogging_table.delete_a_record(record)
        else:
            msg = f'Permission Denied: {token_owner} can not delete record {rid}'
            logger.error(msg)
            raise exceptions.NoAccessError(msg)

    def clear_record_table(self):
        self.jogging_table.clear()

    def make_weekly_report(self, token, week_start_date):
        """Given a token and a week_start_date, return a jogging report for that user in that week

        :param token:
            a login token
        :param week_start_date:
            a Monday date to indicate the start of that week

        :return:
            a dict of total distance, total run time and average speed
        """
        week_end_date = week_start_date + datetime.timedelta(days=6)
        filter_dict = {
            'and': [
                {'field': 'date', 'op': '>=', 'value': week_start_date},
                {'field': 'date', 'op': '<=', 'value': week_end_date},
            ]
        }
        records = self.read_all_records_of_a_user(token, filter_dict)
        total_distance = 0
        total_time = 0
        for r in records:
            total_distance += r['distance']
            total_time += r['time']

        return {'total_distance(meters)': total_distance, 'total_time(minutes)': total_time, 'speed': total_distance / total_time}


if os.environ.get('IN_MEMORY_DB'):
    dbs = DBService('test', in_memory=True)
else:
    dbs = DBService('test7.db')
