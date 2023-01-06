from flask import Flask, request, jsonify, render_template ,make_response
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from models.models import db, User, Train , Home , Type_Class ,Ticket
from  werkzeug.security import generate_password_hash, check_password_hash
from Validate import Validate
import uuid
import json
from datetime import date, datetime
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask_cors import CORS
import random


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:%s@localhost/booking' % quote_plus('bala')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.config['SECRET_KEY'] = 'your secret key'

jsondecoder = json.JSONDecoder()


@app.route("/", methods=['POST', 'GET'])
def root():
    print("Welcome Train Booking")
    return make_response(jsonify({'message' : "Welcome To Train Booking"}), 200)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return make_response(
            jsonify({'message' : 'Token is missing !!'}),
            401) 
        print(token)
        token = str.replace(str(token), "Bearer ", "")
        try:
            #token = jsondecoder.decode(token)
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            print(data)
            current_user = User.query.filter_by(public_id = data['public_id']).first()
            if current_user.validity == 0:
                return make_response(
                jsonify({'message' : 'User Logged Out..Need to Login'}),
                401)
            print(current_user)
        except Exception as e:
            print(".....!!!!!.... ", e)
            return make_response(
            jsonify({'message' : 'Token is invalid !!'}),
            401)
        print(token)
        return  f(current_user, *args, **kwargs)
    return decorated

#   Signup

@app.route("/user/signup", methods = ['POST','GET'])
def user_insert():
    data = request.form
    
    if not data or not data.get('username') or not data.get('password') or not data.get('userType') or not data.get('email') :
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401
            )
    if not data.get('firstName') or not data.get('lastName') or not data.get('dob'):
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401
            )

    password = data.get('password')       
    user_name , email = data.get('username') , data.get('email')
    first_name , last_name = data.get('firstName') , data.get('lastName')
    user_type = data.get('userType')
    dob = data.get('dob')

    birthdate = datetime.strptime(dob , "%Y-%m-%d")
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    print(age)
    
    user = User.query.filter_by(user_name = user_name).first() or  User.query.filter_by(email = email).first()
    if user:
        return make_response(
            jsonify({"status" : "User Already Exists"}),
            401
            )
    
    password= generate_password_hash(data["password"])
    public_id = str(uuid.uuid4())
    record = User(public_id,first_name,last_name,user_name,email,dob,age,user_type,password,0)
    db.session.add(record)
    db.session.commit()
    return make_response(
            jsonify({"status" : "Successfully Created"}),
            200
            )

#   Login

@app.route("/user/login" , methods = ['POST','GET'])
def login():
    data = request.form
    
    if not data or not data.get('username') or not data.get('password'):
        return make_response(
            jsonify({"status" : "Feilds missing"}),
            401
            )
    user_name = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(user_name = user_name).first()
    print(user,type(user))
    if not user:
        return make_response(
            jsonify({"status" : "User not found"}),
            401
            )
    
    if check_password_hash(user.password, password):
        jwt_token = jwt.encode({
            'public_id': user.public_id,
            'exp' : datetime.utcnow() + timedelta(minutes = 3000)
            }, app.config['SECRET_KEY'],"HS256")
        setattr(user, "validity", 1)
        db.session.commit()
        return make_response(
            jsonify({"status" : "Success", "token" : jwt_token}),
            200)
    else:
        return make_response(
            jsonify({"status" : "Wrong password"}),
            401)

#   Home

@app.route("/user/home", methods = ['POST','GET'])
@token_required
def home(current_user):
    data = request.get_json()
    temp = {} 
    output = []
    
    if not Validate.json(data, ["trainfrom","trainto","class","type","date","trainavailable"]):
        return make_response(
            jsonify({"status" : "Fields Missing"}),
            401)
    
    record = Home(data["trainfrom"],data["trainto"],data["class"],data["type"],data["date"],data["trainavailable"]) 
    db.session.add(record)
    db.session.commit()
    
    if Validate.isPresent(db, Train, "train_from", data["trainfrom"]) and\
        Validate.isPresent(db, Train, "train_to", data["trainto"]):
        
        train_check = db.session.query(Train.start_time, Train.total_tickets,Train.start_date, Train.train_name, Train.train_from, Train.train_to, Type_Class.train_class,Type_Class.no_of_tickets).join(Type_Class,Train.train_name == Type_Class.train_name).all()
        print(train_check,type(train_check),type(train_check[0]))
        
        for i in train_check:
            if i.train_from == data["trainfrom"] and i.train_to == data["trainto"] and\
                i.train_class == data["class"] and i.start_date ==  data["date"]:
                    if (data["trainavailable"] == "yes" and i.no_of_tickets > 0) or data["trainavailable"] == "no": 
                        temp = {}
                        temp["trainname"] =i.train_name
                        temp["time"] = i.start_time
                        temp["date"] = i.start_date
                        temp["no_of_tickets"] = i.total_tickets
                        temp["trainfrom"] = i.train_from
                        temp["trainto"] = i.train_to
                        temp["class"] = i.train_class  
                        output.append(temp)
                        print(output)
        print(output)
    else:
        return make_response(
            jsonify({"status" : "Train Details Missing"}),
            401)   
    print(output)
    return output

# Ticket

@app.route("/ticket/insert", methods = ['POST','GET'])
@token_required
def ticket(current_user):
    data = request.form

    if not data or not data.get('noofticket') or not data.get('price') or not data.get('trainid') or not data.get('bookingstatus'):
        return make_response(
            jsonify({"status" : "Feilds missing.."}),
            401)
    
    train_id = data.get('trainid')
    no_of_ticket_booked = int(data.get('noofticket')) 
    price = int(data.get('price'))
    ticket_status = data.get('bookingstatus')
    print(price,type(price))

    user_ticket_count = no_of_ticket_booked
    
    user = User.query.filter_by(user_name = current_user.user_name).first()
    print(user,type(user))
    if not user:
        return make_response(
            jsonify({"status" : "User not found"}),
            401
            )
    
    if not Validate.isPresent(db, Train, "id", train_id):
        return make_response(
            jsonify({"status" : "Foreign Key Constraint(Train ID)"}),
            401)
    
    # user_ticket = Ticket.query.filter_by(user_name = current_user.user_name).all()
    # if user_ticket:
    #     for i in user_ticket:
    #         user_ticket_count = user_ticket_count + i.no_of_ticket_booked  
    if user_ticket_count > 6:
        return make_response(
            jsonify({"status" : "User can register only 6 tickets maximum"}),
            401)
    
    pnr = random.randint((10**7)+1,10**8)
    pnr = int(str(pnr)+str(current_user.id))
    
    record = Ticket(pnr,current_user.user_name,train_id,no_of_ticket_booked,price,ticket_status)
    db.session.add(record)
    db.session.commit()
    return make_response(
            jsonify({"status" : "Successfully Created"}),
            200)
    
@app.route("/pnr", methods = ['POST','GET'])
@token_required
def pnr(current_user):
    data = request.get_json()
    
    if not Validate.json(data, ["pnr"]):
        return make_response(
            jsonify({"status" : "PNR Number Missing"}),
            404)
    if not Validate.isPresent(db, Ticket, "pnr" ,data["pnr"]):
        return make_response(
            jsonify({"status" : "PNR Not Found"}),
            404)
    
    temp = Ticket.query.filter_by(pnr = data["pnr"]).first()
    output = {}
    output["pnr"] = temp.pnr
    output["username"] = temp.user_name
    output["ticketstatus"] = temp.ticket_status
    
    user = Train.query.filter_by(id = temp.train_id).first()
    output["trainname"] = user.train_name
    output["trainfrom"] = user.train_from
    output["trainto"] = user.train_to
    output["time"] = user.start_time 
    output["date"] = user.start_date  
    
    return output

@app.route("/logout" , methods=['POST','GET'])
@token_required
def logout(current_user):
    setattr(current_user, "validity", 0)
    db.session.commit()
    return make_response(
        jsonify({'message' : 'Logged Out'}),
        200)