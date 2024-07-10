from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    '''
    User model to store user details
    '''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    motto = db.Column(db.String(255), nullable=True)
