from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    mobile = db.Column(db.Integer)
    email = db.Column(db.String(100))
    password = db.Column(db.String(256))
    gender = db.Column(db.String(10))
    addr = db.Column(db.String(100))
    
    def __init__(self, id , user_name, age, mobile, email, password, gender, addr):
        self.id = id
        self.user_name = user_name
        self.age = age
        self.mobile = mobile
        self.email = email
        self.password = password
        self.gender = gender
        self.addr = addr
    
    