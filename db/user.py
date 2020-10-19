import uuid
import hashlib
from db.models import UserInfo
from filtering.filters import apply_filters


class UserTable:
    def __init__(self, session):
        self.session = session

    def login(self, username, password):
        encrypted_pw = hashlib.sha1(password.encode()).hexdigest()

        user = self.session.query(UserInfo).filter(UserInfo.username == username, UserInfo.password == encrypted_pw).one()
        if user:
            token = str(uuid.uuid4())
            params = {
                'token': token,
                'username': username,
            }
            self.update_a_user(params)
            return token

    def create_a_user(self, params):
        self.session.add(UserInfo(**params))
        self.session.commit()

    def delete_a_user(self, user):
        """Given a user object, delete it from user table
        :param user: user object
        :return:
        """
        self.session.delete(user)
        self.session.commit()

    def clear(self):
        """Delete all rows in user table

        :return:
        """
        self.session.query(UserInfo).delete()
        self.session.commit()

    def update_a_user(self, params):
        record = self.session.query(UserInfo).filter(UserInfo.username == params['username']).one()
        for k, v in params.items():
            if k != 'username':
                setattr(record, k, v)

        self.session.commit()

    def get_a_user_by_token(self, token):
        return self.session.query(UserInfo).filter(UserInfo.token == token).one()

    def get_a_user_by_un_and_pw(self, username, password):
        return self.session.query(UserInfo).filter(UserInfo.username == username, UserInfo.password == password).one()

    def get_a_user_by_username(self, username):
        return self.session.query(UserInfo).filter(UserInfo.username == username).one()

    def get_all_users(self, filters):
        return apply_filters(self.session.query(UserInfo), filters)
