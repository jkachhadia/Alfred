from . import db
from flask import request
from datetime import datetime

class Event(db.Model):
    __tablename__='events'
    id=db.Column(db.Integer,primary_key=True)
    sender_id=db.Column(db.String(100))
    name=db.Column(db.String(100),default='event')
    date=db.Column(db.Date)
    reminded=db.Column(db.Boolean,default=False)
