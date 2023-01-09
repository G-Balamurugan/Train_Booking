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
    validity = db.Column(db.Integer)

    def __init__(self,public_id , first_name, last_name, user_name, email, dob, age, user_type, password, validity):
        self.public_id = public_id 
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = user_name
        self.email = email
        self.dob = dob
        self.age = age
        self.user_type = user_type
        self.password = password
        self.validity = validity
    

class Train(db.Model):
    
    __tablename__ = "train"
    
    id = db.Column(db.Integer, primary_key = True) 
    train_name = db.Column(db.String(40))
    start_time = db.Column(db.String(40))
    end_time = db.Column(db.String(40))
    duration = db.Column(db.String(20))
    train_from = db.Column(db.String(30))
    train_to = db.Column(db.String(30))
    no_of_compartment = db.Column(db.Integer)
    no_of_tickets_compartment = db.Column(db.Integer)
    start_date = db.Column(db.String(30))
    end_date = db.Column(db.String(30))
    total_tickets = db.Column(db.Integer)

    def __init__(self, train_name, start_time, end_time, duration, train_from, train_to, start_date, end_date, no_of_compartment, no_of_tickets_compartment, total_tickets):
        self.train_from = train_from
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration
        self.train_name = train_name
        self.train_to = train_to
        self.start_date = start_date
        self.end_date = end_date
        self.no_of_compartment = no_of_compartment
        self.no_of_tickets_compartment = no_of_tickets_compartment
        self.total_tickets = total_tickets 
        
class Type_Class(db.Model):
    
    __tablename__ = "type_class"
    
    id = db.Column(db.Integer, primary_key = True) 
    train_name = db.Column(db.String(40))
    train_class = db.Column(db.String(100))
    no_of_compartment = db.Column(db.Integer)
    price = db.Column(db.Integer)
    
    def __init__(self, train_name, train_class, no_of_compartment, price):
        self.train_name = train_name
        self.train_class = train_class
        self.no_of_compartment = no_of_compartment
        self.price = price
        
class Home(db.Model):
    
    __tablename__ = "home"
    
    id = db.Column(db.Integer, primary_key = True)
    train_from = db.Column(db.String(30))
    train_to = db.Column(db.String(30))
    train_class = db.Column(db.String(30))
    train_type = db.Column(db.String(30)) 
    train_date = db.Column(db.String(30))
    train_available = db.Column(db.String(10))
    
    def __init__(self, train_from, train_to, train_class, train_type, train_date, train_available):
        self.train_from = train_from
        self.train_to = train_to
        self.train_class = train_class
        self.train_type = train_type
        self.train_date = train_date
        self.train_available = train_available

class Ticket_Booking(db.Model):
    
    __tablename__ = "ticket_booking"
    
    id = db.Column(db.Integer, primary_key = True)
    train_id = db.Column(db.Integer, db.ForeignKey("train.id"))
    train_name = db.Column(db.String(30))
    train_class = db.Column(db.String(30))
    ticket_type = db.Column(db.String(30))
    no_of_tickets_required = db.Column(db.Integer) 
    
    def __init__(self, train_id, train_name, train_class, ticket_type, no_of_tickets_required):
        self.train_id = train_id
        self.train_name = train_name
        self.train_class = train_class
        self.ticket_type = ticket_type
        self.no_of_tickets_required = no_of_tickets_required
        
class Seat_Remaining(db.Model):
    
    __tablename__ = "seat_remaining"
    
    id = db.Column(db.Integer, primary_key = True)
    train_id = db.Column(db.Integer , db.ForeignKey("train.id"))
    train_class = db.Column(db.String(30))
    total_class_seat = db.Column(db.Integer)
    seat_start_no = db.Column(db.Integer)
    
    def __init__(self, train_id,train_class,total_class_seat,seat_start_no):
        self.train_id = train_id
        self.train_class = train_class
        self.total_class_seat = total_class_seat
        self.seat_start_no = seat_start_no

class Ticket(db.Model):
    
    __tablename__ = "ticket"
    
    id = db.Column(db.Integer, primary_key = True)
    pnr = db.Column(db.Integer)
    user_name = db.Column(db.String(100))
    train_id = db.Column(db.Integer , db.ForeignKey("train.id"))
    seat_no = db.Column(db.Integer)
    price = db.Column(db.Integer)
    ticket_status = db.Column(db.String(50))
    
    def __init__(self, pnr, user_name, train_id, seat_no, price, ticket_status):
        self.pnr = pnr
        self.user_name = user_name
        self.train_id = train_id
        self.seat_no = seat_no
        self.price = price
        self.ticket_status = ticket_status
