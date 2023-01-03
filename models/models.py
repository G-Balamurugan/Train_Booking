from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(256))
    user_type = db.Column(db.String(20))

    def __init__(self, user_name, email, user_type, password):
        self.user_name = user_name
        self.email = email
        self.user_type = user_type
        self.password = password
    
class Passenger(db.Model):
    
    __tablename__ = "passenger"
    
    id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    booking_status = db.Column(db.String(100))
    
    def __init__(self, id, user_name, email, booking_status):
        self.id = id
        self.user_name = user_name
        self.email = email
        self.booking_status = booking_status

        
     