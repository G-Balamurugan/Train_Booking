from flask import Flask, request, jsonify, render_template ,make_response
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from models.models import db, User, Train , Home , Type_Class
from  werkzeug.security import generate_password_hash, check_password_hash
from Validate import Validate
import uuid
import json
from datetime import date, datetime
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:%s@localhost/booking' % quote_plus('bala')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.config['SECRET_KEY'] = 'your secret key'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return make_response(
            jsonify({'message' : 'Token is missing !!'}),
            401
            ) 
        token = str.replace(str(token), "Bearer ", "")
        print(token)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithm=["HS256"])
            current_user = User.query.filter_by(public_id = data['public_id']).first()
        except:
            return make_response(
            jsonify({'message' : 'Token is invalid !!'}),
            401
            )
        return  f(current_user, *args, **kwargs)
    return decorated


@app.route("/")
def root():
    print("Welcome Train Booking")
    return make_response(jsonify({'message' : "Welcome To Train Booking"}), 200)

#   Signup
@app.route("/user/signup", methods = ['POST','GET'])
def user_insert():
    data = request.form
    
    if not data or not data.get('user_name') or not data.get('password') or not data.get('user_type') or not data.get('email') :
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401
            )
    if not data.get('first_name') or not data.get('last_name') or not data.get('dob'):
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401
            )

    password = data.get('password')       
    user_name , email = data.get('user_name') , data.get('email')
    first_name , last_name = data.get('first_name') , data.get('last_name')
    user_type = data.get('user_type')
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
    record = User(public_id,first_name,last_name,user_name,email,dob,age,user_type,password)
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
def home():
    data = request.get_json()
    
    temp = {}
    output = []
    
    if not Validate.json(data, ["trainfrom","trainto","class","type","date","trainavailable"]):
        return make_response(
            jsonify({"status" : "Fields Missing"}),
            401
            )
    
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
                    temp["trainname"] =i.train_name
                    temp["time"] = i.start_time
                    temp["date"] = i.start_date
                    temp["no_of_tickets"] = i.total_tickets
                    temp["trainfrom"] = i.train_from
                    temp["trainto"] = i.train_to
                    temp["class"] = i.train_class  
                    output.append(temp)
        print(output)
    else:
        return make_response(
            jsonify({"status" : "Train Details Missing"}),
            401
            )   
    return output