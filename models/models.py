from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    public_id = db.Column(db.String(256))
    user_name = db.Column(db.String(100))
    dob = db.Column(db.DateTime)
    email = db.Column(db.String(100))
    password = db.Column(db.String(256))
    user_type = db.Column(db.String(20))

    def __init__(self,public_id , first_name, last_name, user_name, email, dob, user_type, password):
        self.public_id = public_id 
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = user_name
        self.email = email
        self.dob = dob
        self.user_type = user_type
        self.password = password
    
class Passenger(db.Model):
    
    __tablename__ = "passenger"
    
    id = db.Column(db.Integer, primary_key = True)
    public_id = db.Column(db.String(256))
    user_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    booking_status = db.Column(db.String(100))
    
    def __init__(self, id, user_name, email, booking_status):
        self.id = id
        self.user_name = user_name
        self.email = email
        self.booking_status = booking_status

        
     