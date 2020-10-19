from db.models import JoggingInfo
from filtering.filters import apply_filters


class JoggingTable:
    def __init__(self, session):
        self.session = session

    def create_a_record(self, params):
        self.session.add(JoggingInfo(**params))
        self.session.commit()

    def delete_a_record(self, record):
        self.session.delete(record)
        self.session.commit()

    def clear(self):
        """Delete all rows in jogging table

        :return:
        """
        self.session.query(JoggingInfo).delete()
        self.session.commit()

    def update_a_record(self, params):
        record = self.session.query(JoggingInfo).filter(JoggingInfo.rid == params['rid']).one()
        for k, v in params.items():
            if k not in ['rid', 'username']:
                setattr(record, k, v)

        self.session.commit()

    def get_a_record_by_id(self, rid):
        return self.session.query(JoggingInfo).filter(JoggingInfo.rid == rid).one()

    def get_all_records(self, filter_dict):
        """Given a filter dict, return filtered records.
        
        :param filter_dict: a dict of filters
        :return: a list of record dicts
        """
        records = apply_filters(self.session.query(JoggingInfo), filter_dict)
        return [r.to_dict() for r in records]

    def get_records_of_a_user(self, username, filter_dict):
        """Given a usename and a filter dict, return filtered records that belongs to the user.

        :param username: a username of a user
        :param filter_dict: a dict of filters

        :return: a list of record objects
        """
        if filter_dict:
            filter_dict = {
                'and': [
                    {'field': 'username', 'op': '==', 'value': username},
                    filter_dict,
                ]
            }
        else:
            filter_dict = {'field': 'username', 'op': '==', 'value': username}

        records = apply_filters(self.session.query(JoggingInfo), filter_dict)
        return [r.to_dict() for r in records]
