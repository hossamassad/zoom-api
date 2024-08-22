from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from flask_appbuilder.security.sqla.models import User
from flask_appbuilder import Model

class Supervisor(Model):

    __tablename__ = 'supervisor'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('ab_user.id'))
    supervisor_id = Column(Integer, ForeignKey('ab_user.id'))

    user = relationship('User', foreign_keys=[user_id], backref='supervisee')
    supervisor = relationship('User', foreign_keys=[supervisor_id], backref='supervisor')