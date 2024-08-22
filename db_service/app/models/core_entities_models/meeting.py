from sqlalchemy import Column, Integer, String, DateTime
from marshmallow import Schema, fields, post_load
from flask_appbuilder import Model

class Meeting(Model):
    __tablename__ = 'meeting'
    id = Column(Integer, primary_key=True)
    meeting_id = Column(Integer, unique=True, nullable=False)
    uuid = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)
    timezone = Column(String, nullable=False)
    agenda = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    start_url = Column(String, nullable=False)
    join_url = Column(String, nullable=False)
    encrypted_password = Column(String, nullable=False)

    def __repr__(self):
        return f'<Meeting {self.id}>'

class MeetingSchema(Schema):
    id = fields.Int(dump_only=True)
    meeting_id = fields.Int(required=True)
    uuid = fields.Str(required=True)
    topic = fields.Str(required=True)
    start_time = fields.DateTime(required=True)
    duration = fields.Int(required=True)
    timezone = fields.Str(required=True)
    agenda = fields.Str()
    created_at = fields.DateTime(required=True)
    start_url = fields.Str(required=True)
    join_url = fields.Str(required=True)
    encrypted_password = fields.Str(required=True)

    @post_load
    def make_meeting(self, data, **kwargs):
        return Meeting(**data)
