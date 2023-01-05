from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    public_id = db.Column(db.String(256))
    user_name = db.Column(db.String(100))
    dob = db.Column(db.String(100))
    email = db.Column(db.String(100))
    age = db.Column(db.Integer)
    password = db.Column(db.String(256))
    user_type = db.Column(db.String(20))

    def __init__(self,public_id , first_name, last_name, user_name, email, dob, age, user_type, password):
        self.public_id = public_id 
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = user_name
        self.email = email
        self.dob = dob
        self.age = age
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

class Train(db.Model):
    
    __tablename__ = "train"
    
    id = db.Column(db.Integer, primary_key = True) 
    train_name = db.Column(db.String(40))
    start_time = db.Column(db.String(40))
    end_time = db.Column(db.String(40))
    duration = db.Column(db.String)
    train_from = db.Column(db.String(30))
    train_to = db.Column(db.String(30))
    start_date = db.Column(db.String(30))
    end_date = db.Column(db.String(30))
    total_tickets = db.Column(db.Integer)

    def __init__(self, train_name, start_time, end_time, duration, train_from, train_to, date, no_of_tickets):
        self.train_from = train_from
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.train_name = train_name
        self.train_to = train_to
        self.start_date = start_date
        self.end_date = end_date
        self.total_tickets = total_tickets 

class Type_Class(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    train_name = db.Column(db.String(40))
    train_class = db.Column(db.String(100))
    train_type = db.Column(db.String(100))
    no_of_tickets = db.Column(db.Integer)
    
    def __init__(self, train_name, train_class, train_type, no_of_tickets):
        self.train_name = train_name
        self.train_class = train_class
        self.train_type = train_type
        self.no_of_tickets = no_of_tickets