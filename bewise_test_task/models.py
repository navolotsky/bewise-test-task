from sqlalchemy import func
from sqlalchemy_serializer import SerializerMixin

from . import db


class Question(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    pulled_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    question_id = db.Column(db.Integer, unique=True, nullable=False)
    # not `String` because max length is unknown
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    airdate = db.Column(db.DateTime(timezone=True), nullable=False)
