from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class login_info(db.Model, UserMixin):
    email = db.Column(db.String(100), primary_key=True, unique=True)
    password = db.Column(db.String(100))
