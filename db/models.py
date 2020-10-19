from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class UserInfo(Base):
    __tablename__ = 'user_info'

    username = Column(String, primary_key=True)
    password = Column(String)
    forename = Column(String)
    surname = Column(String)
    email = Column(String)
    role = Column(String, default='user')
    token = Column(String, default='')

    def __repr__(self):
        return f"<User('{self.username}')>"

    def to_dict(self):
        return {
            'username': self.username,
            'forename': self.forename,
            'surname': self.surname,
            'email': self.email,
            'role': self.role,
            'token': self.token,
        }


class JoggingInfo(Base):
    __tablename__ = 'jogging_info'

    rid = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey('user_info.username'), nullable=False)
    date = Column(Date)
    lat = Column(Float)
    lon = Column(Float)
    distance = Column(Integer)  # meter
    time = Column(Integer)  # minute
    weather = Column(String)

    def __repr__(self):
        return f"<JoggingInfo(username='{self.username}', rid='{self.rid}'))>"

    def to_dict(self):
        return {
            'rid': self.rid,
            'username': self.username,
            'date': self.date,
            'lat': self.lat,
            'lon': self.lon,
            'distance': self.distance,
            'time': self.time,
            'weather': self.weather,
        }
